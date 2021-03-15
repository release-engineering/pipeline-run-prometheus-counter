# Pipeline Run Prometheus Counter

Expose counter metrics for various pipeline runs for the Prometheus text format.

This is useful if you have a pipeline such as Tekton or Jenkins and you need
to keep track of success and/or failure rates of Pipeline runs in Prometheus.

These pipeline runs are stored in a simple SQLite database.

## HTTP Endpoints

You may view the Prometheus metrics at the `/metrics` endpoint. The ouput
will be in the following format:

```text
# HELP car_factory_pipeline_run_total The total number of car_factory pipeline runs.
# TYPE pipeline_tests_pipeline_run_total counter
car_factory_pipeline_run_total{status="success"} 1
car_factory_pipeline_run_total{status="failure"} 1
```

To add a pipeline run, submit a POST request to the `/metrics` endpoint with
the `name` and `success` properties. For example:

```json
{
    "name": "car_factory",
    "success": true
}
```

## Configuration

The path to the SQLite database is configured by the `PRPC_DB_PATH`
environment variable. This defaults to `prpc.db` in the current directory of
execution.
