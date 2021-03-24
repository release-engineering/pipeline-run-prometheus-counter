# SPDX-License-Identifier: GPL-3.0-or-later
import textwrap

import pytest


def test_get_metrics(client, db):
    for name, success in (
        ("car_factory", True),
        ("car_factory", False),
        ("truck_factory", True),
        ("truck_factory", True),
    ):
        db.add_pipeline_run(name, success)

    response = client.get("/metrics")
    assert response.status_code == 200
    text = response.data.decode("utf-8")
    assert text == textwrap.dedent(
        """\
        # HELP car_factory_pipeline_run_total The total number of car_factory pipeline runs.
        # TYPE car_factory_pipeline_run_total counter
        car_factory_pipeline_run_total{status="success"} = 1
        car_factory_pipeline_run_total{status="failure"} 1
        # HELP truck_factory_pipeline_run_total The total number of truck_factory pipeline runs.
        # TYPE truck_factory_pipeline_run_total counter
        truck_factory_pipeline_run_total{status="success"} = 2
        truck_factory_pipeline_run_total{status="failure"} 0
        """
    )


@pytest.mark.parametrize("success", (True, False))
def test_add_pipeline_run(success, client, db):
    assert db.get_pipeline_runs_count() == {}

    response = client.post("/metrics", json={"name": "car_factory", "success": success})

    assert response.status_code == 201
    assert response.json == {"name": "car_factory", "success": success}
    if success:
        total_failure = 0
        total_success = 1
    else:
        total_failure = 1
        total_success = 0

    assert db.get_pipeline_runs_count() == {
        "car_factory": {"failure": total_failure, "success": total_success}
    }


@pytest.mark.parametrize("authorization", ("", "Bearer my_token", "PRPC my_token"))
def test_add_pipeline_run_unauthorized(authorization, app, client, db):
    app.config["PRPC_PSK"] = "L3tM3!n"
    assert db.get_pipeline_runs_count() == {}

    response = client.post(
        "/metrics",
        json={"name": "car_factory", "success": True},
        headers={"Authorization": authorization},
    )

    assert response.status_code == 401
    assert db.get_pipeline_runs_count() == {}


def test_add_pipeline_run_authorized(app, client, db):
    app.config["PRPC_PSK"] = "L3tM3!n"
    assert db.get_pipeline_runs_count() == {}

    response = client.post(
        "/metrics",
        json={"name": "car_factory", "success": True},
        headers={"Authorization": "PRPC L3tM3!n"},
    )

    assert response.status_code == 201
    assert db.get_pipeline_runs_count() == {"car_factory": {"failure": 0, "success": 1}}


@pytest.mark.parametrize(
    "payload, error",
    (
        ("Does this thing work?", "The input must be a JSON object"),
        (
            {"best_actor": "Tom Hanks"},
            "The input JSON object must only contain the name and success properties",
        ),
        ({"name": "car_factory", "success": "yes"}, "The success value must be a boolean"),
        ({"name": 3, "success": True}, "The name value must be a string"),
    ),
)
def test_add_pipeline_run_invalid(payload, error, client, db):
    assert db.get_pipeline_runs_count() == {}

    response = client.post("/metrics", json=payload)

    assert response.status_code == 400
    assert response.json == {"error": error}
    assert db.get_pipeline_runs_count() == {}
