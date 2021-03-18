# SPDX-License-Identifier: GPL-3.0-or-later
import prpc.app
import prpc.db

app = prpc.app.create_app()
db = prpc.db.DBConnection(app.config["PRPC_DB_PATH"])
db.create_tables()
