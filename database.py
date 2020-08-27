"""Manage access to the database."""

import pymysql
import logging,sys,traceback, datetime

class Database:
    """Database access."""

    def __init__(self,config):
        """Constructor."""
        self._database = None
        self._config = config
    
    def __del__(self):

         db = getattr(self, '_database', None)
         if db is not None:
                print( "closing db...")
                db.close()

        
    def connect_to_db(self):
        """Open database and return a connection handle."""
        
        c = getattr(self, '_config', None)
        if c.get("DEBUG"):print("init db..")
        
        return pymysql.connect(
                c['MYSQL_DATABASE_HOST'],
                c['MYSQL_DATABASE_USER'],
                c['MYSQL_DATABASE_PASSWORD'],
                c['MYSQL_DATABASE_DB'],
                cursorclass=pymysql.cursors.DictCursor
            )

    def get_db(self):
        """Return the global db connection or create one."""
        db = getattr(self, '_database', None)

        if db is None:
            db = self._database = self.connect_to_db()

        return db

    def query_db(self, query, args=(), one=False):
        """Query the database."""
        with self.get_db().cursor() as cur:
            cur.execute(query, args)
            rv = cur.fetchall()
            cur.close()
        if self._config.get("DEBUG"):print(cur._last_executed)

        return (rv[0] if rv else None) if one else rv

    def query_db_commit(self, query, args=(), one=False):
        """Query the database."""
        with self.get_db().cursor() as cur:
            cur.execute(query, args)
            rv = cur.fetchall()
            cur.close()
        self.get_db().commit()
        return (rv[0] if rv else None) if one else rv


    def insert_db(self, query, args=(), one=False):
        """Query the database for insert."""
        try:
            with self.get_db().cursor() as cur:
                cur.execute(query, args)
                #print("affected rows = {}").format(cur.rowcount)
                cur.close()
            self.get_db().commit()
            return True
        except:
            logging.debug(traceback.print_exc(file=sys.stdout))
