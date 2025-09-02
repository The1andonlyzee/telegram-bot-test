import pymysql
import logging
from config.settings import MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB, MYSQL_PORT

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