
from trac.core import *
from trac.env import IEnvironmentSetupParticipant
from trac.db import DatabaseManager
from trac.web.chrome import ITemplateProvider
from trac.web import ITemplateStreamFilter

import db_default

class WechatLoginSystem(Component):


    implements(IEnvironmentSetupParticipant)

    def __init__(self):
        self.found_db_version = 0

    # IEnvironmentSetupParticipant methods
    def environment_created(self):
        self.upgrade_environment()

    def environment_needs_upgrade(self, db):
        cursor = db.cursor()
        cursor.execute("""
                    SELECT value FROM system WHERE name=%s
                    """, (db_default.name,))
        value = cursor.fetchone()
        try:
            self.found_db_version = int(value[0])
            if self.found_db_version < db_default.version:
                return True
        except:
            return True

        return False

    def upgrade_environment(self, db=None):
        db_manager, _ = DatabaseManager(self.env)._get_connector()
        # update the version
        with self.env.db_transaction as db:
            old_data = {}  # {table.name: (cols, rows)}
            cursor = db.cursor()
            if not self.found_db_version:
                cursor.execute("""
                     INSERT INTO system (name, value) VALUES (%s, %s)
                     """, (db_default.name, db_default.version))
            else:
                cursor.execute("""
                     UPDATE system SET value=%s WHERE name=%s
                     """, (db_default.version, db_default.name))

                for table in db_default.tables:
                    cursor.execute("""
                         SELECT * FROM """ + table.name)
                    cols = [x[0] for x in cursor.description]
                    rows = cursor.fetchall()
                    old_data[table.name] = (cols, rows)
                    cursor.execute("""
                         DROP TABLE """ + table.name)

            # insert the default table
            for table in db_default.tables:
                for sql in db_manager.to_sql(table):
                    cursor.execute(sql)

                # add old data
                if table.name in old_data:
                    cols, rows = old_data[table.name]
                    sql = """
                         INSERT INTO %s (%s) VALUES (%s)
                         """ % (table.name, ','.join(cols), ','.join(['%s'] * len(cols)))
                    for row in rows:
                        cursor.execute(sql, row)

