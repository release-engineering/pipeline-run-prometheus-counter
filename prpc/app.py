# SPDX-License-Identifier: GPL-3.0-or-later
import os
import re
import textwrap

import flask
import werkzeug.exceptions

import prpc.db
import prpc.errors

metrics_bp = flask.Blueprint("metrics", __name__)


def create_app():
    """
    Create a configured Flask application object.

    :return: the Flask application object
    :rtype: flask.Flask
    """
    app = flask.Flask(__name__)
    # Use the in-memory SQLite database for tests
    if os.environ.get("PRPC_TESTING", "").lower() == "true":
        db_path = ":memory:?cache=shared"
    else:
        current_dir = os.path.abspath(os.path.curdir)
        db_path = os.path.join(current_dir, "prpc.db")
    app.config["PRPC_DB_PATH"] = os.environ.get("PRPC_DB_PATH", db_path)
    # Pre-shared key for authentication. Omit this value if authentication should be disabled.
    app.config["PRPC_PSK"] = os.environ.get("PRPC_PSK")
    app.register_blueprint(metrics_bp)

    for code in werkzeug.exceptions.default_exceptions.keys():
        app.register_error_handler(code, prpc.errors.json_error)
    app.register_error_handler(prpc.errors.ValidationError, prpc.errors.json_error)

    def _start_db():
        flask.g.db = prpc.db.DBConnection(app.config["PRPC_DB_PATH"])

    # Create a database connection object before the request starts.
    # The connection won't actually open up until it's first used.
    # This will be automatically cleaned up after the request is torn down
    # by the garbage collector.
    app.before_request(_start_db)

    return app


@metrics_bp.route("/metrics")
def metrics():
    """Display Prometheus metrics related to the pipelines."""
    all_total_runs = flask.g.db.get_pipeline_runs_count()

    metrics_content = ""
    # Sort by pipeline name so it is consistent ordering
    for name in sorted(all_total_runs.keys()):
        pipline_runs = all_total_runs[name]
        metrics_content += textwrap.dedent(
            f"""\
            # HELP {name}_pipeline_run_total The total number of {name} pipeline runs.
            # TYPE {name}_pipeline_run_total counter
            {name}_pipeline_run_total{{status="success"}} {pipline_runs["success"]}
            {name}_pipeline_run_total{{status="failure"}} {pipline_runs["failure"]}
            """
        )
    return flask.Response(metrics_content, content_type="text/plain; charset=utf-8")


@metrics_bp.route("/metrics", methods=["POST"])
def add_pipeline_run():
    """Add a pipeline run."""
    if flask.current_app.config["PRPC_PSK"]:
        failure_msg = (
            'The Authorization header must be provided in the format of "PRPC <pre-shared key>"'
        )
        authz = flask.request.headers.get("Authorization")
        if not authz:
            raise werkzeug.exceptions.Unauthorized(failure_msg)
        if not re.match(r"PRPC .+", authz):
            raise werkzeug.exceptions.Unauthorized(failure_msg)

        psk = authz.split(" ", 1)[1]
        if psk != flask.current_app.config["PRPC_PSK"]:
            raise werkzeug.exceptions.Unauthorized("The provided pre-shared key is incorrect")

    payload = flask.request.get_json(force=True)
    if not isinstance(payload, dict):
        raise prpc.errors.ValidationError("The input must be a JSON object")

    if payload.keys() != {"name", "success"}:
        raise prpc.errors.ValidationError(
            "The input JSON object must only contain the name and success properties"
        )

    if not isinstance(payload["success"], bool):
        raise prpc.errors.ValidationError("The success value must be a boolean")

    if not isinstance(payload["name"], str):
        raise prpc.errors.ValidationError("The name value must be a string")

    flask.g.db.add_pipeline_run(payload["name"], payload["success"])

    return flask.jsonify(payload), 201


if __name__ == "__main__":
    app = create_app()
    db = prpc.db.DBConnection(app.config["PRPC_DB_PATH"])
    db.create_tables()
    app.run(debug=True)
