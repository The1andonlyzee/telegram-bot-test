import pymysql
import logging
from config.settings import MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB, MYSQL_PORT
from contextlib import contextmanager
import time

logger = logging.getLogger(__name__)

class BaseDatabase:
    """Base database class with common connection functionality"""
    
    def __init__(self):
        self.connection_params = {
            'host': MYSQL_HOST,
            'user': MYSQL_USER,
            # 'port': MYSQL_PORT,
            'password': MYSQL_PASS,
            'db': MYSQL_DB,
            'cursorclass': pymysql.cursors.DictCursor,
            'connect_timeout': 10
        }
    
    def get_connection(self):
        """Get database connection"""
        try:
            return pymysql.connect(**self.connection_params)
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    @contextmanager
    def get_db_connection(self):
        """Context manager for database connections"""
        connection = None
        try:
            connection = self.get_connection()
            yield connection
        except Exception as e:
            logger.error(f"Database error in context manager: {e}")
            if connection:
                try:
                    connection.rollback()
                except:
                    pass
            raise
        finally:
            if connection:
                try:
                    connection.close()
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")
    
    def execute_query(self, query, params=None):
        """Execute a single query and return results"""
        with self.get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
    