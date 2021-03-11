# SPDX-License-Identifier: GPL-3.0-or-later
import flask
import werkzeug.exceptions


class ValidationError(Exception):
    """Raised when user input is invalid."""


def json_error(error):
    """
    Convert exceptions to JSON responses.

    :param Exception error: an Exception to convert to JSON
    :return: a Flask JSON response
    :rtype: flask.Response
    """
    if isinstance(error, werkzeug.exceptions.HTTPException):
        response = flask.jsonify({"error": error.description})
        response.status_code = error.code
    else:
        status_code = 500
        msg = str(error)
        if isinstance(error, ValidationError):
            status_code = 400

        response = flask.jsonify({"error": msg})
        response.status_code = status_code
    return response
