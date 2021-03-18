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

## Dependency Management

To manage dependencies, this project uses [pip-tools](https://github.com/jazzband/pip-tools) so that
the production dependencies are pinned and the hashes of the dependencies are verified during
installation.

The unpinned dependencies are recorded in `setup.py`, and to generate the `requirements.txt` file,
run `pip-compile --generate-hashes --output-file=requirements.txt`. This is only necessary when
adding a new package. To upgrade a package, use the `-P` argument of the `pip-compile` command.

When installing the dependencies in a production environment, run
`pip install --require-hashes -r requirements.txt`. Alternatively, you may use
`pip-sync requirements.txt`, which will make sure your virtualenv only has the packages listed in
`requirements.txt`.

To ensure the pinned dependencies are not vulnerable, this project uses
[safety](https://github.com/pyupio/safety), which runs on every pull-request.
