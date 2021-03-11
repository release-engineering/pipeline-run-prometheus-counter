# SPDX-License-Identifier: GPL-3.0-or-later
import sqlite3


# This class relies on the __del__ method of the SQLite connection object
# to properly clean up the connections. It's not handled directly in the class
# for this reason.
class DBConnection:
    def __init__(self, db_path):
        """
        Manage the database as a context manager.

        :param str db_path: the path to the database that the app is configured to use
        """
        self._db_path = db_path
        self._connection = None

    @property
    def connection(self):
        """Return a started connect to the database."""
        if not self._connection:
            self._connection = sqlite3.connect(f"file:{self._db_path}", uri=True)
        return self._connection

    def create_tables(self):
        """Create the database tables for the application."""
        cursor = self.connection.cursor()
        # Note that SQLite does not support booleans so an integer is used for the success column
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS pipelineRuns (
                name TEXT PRIMARY KEY,
                success INTEGER NOT NULL,
                failure INTEGER NOT NULL
            )
            """
        )
        self.connection.commit()

    def get_pipeline_runs_count(self):
        """
        Get the number of pipeline runs stored in the DB.

        :param bool success: a filter for the ``success`` boolean column
        :returns: a dictionary where the keys are pipeline names and the values
            are dictionaries with the keys failure and success. Those values are
            the number for each respectively.
        :rtype: dict
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT name, success, failure FROM pipelineRuns")
        results = cursor.fetchall()
        rv = {}
        for name, success, failure in results:
            rv[name] = {"success": success, "failure": failure}
        return rv

    def add_pipeline_run(self, name, success):
        """
        Add a pipeline run to the database.

        :param str name: the name of the pipeline
        :param bool success: denotes if the pipline run was successful
        :raises ValidationError: if the success argument is of the wrong type
        """
        inital_success = initial_failure = 0
        if success:
            update_key = "success"
            inital_success = 1
        else:
            update_key = "failure"
            initial_failure = 1

        cursor = self.connection.cursor()
        cursor.execute(
            f"""
            INSERT INTO pipelineRuns (name, success, failure)
            VALUES(?, {inital_success}, {initial_failure})
            ON CONFLICT(name)
            DO UPDATE SET {update_key} = {update_key} + 1
            """,
            (name,),
        )
        self.connection.commit()
