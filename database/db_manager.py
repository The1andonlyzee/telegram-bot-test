import pymysql
import logging
from config.settings import MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB, MYSQL_PORT

logger = logging.getLogger(__name__)

class DatabaseManager:
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
    
    def get_all_locations(self):
        """Get all coverage locations"""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                sql = "SELECT coverage_id, c_name FROM coverage WHERE c_name IS NOT NULL AND c_name != '' ORDER BY c_name"
                cursor.execute(sql)
                results = cursor.fetchall()
                locations = [(row["coverage_id"], row["c_name"]) for row in results if row["c_name"]]
                logger.info(f"Retrieved {len(locations)} unique locations")
                return locations
        except pymysql.Error as e:
            logger.error(f"MySQL error in get_all_locations: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in get_all_locations: {e}")
            return []
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    logger.error(f"Error closing connection in get_all_locations: {e}")
    
    def get_location_data(self, coverage_id):
        """Get ODC and ODP data for port availability"""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                sql = """
                SELECT 
                    c.c_name,
                    odc.code_odc,
                    odp.code_odp,
                    odp.total_port,
                    COALESCE(customer_count.used_ports, 0) as used_ports,
                    (odp.total_port - COALESCE(customer_count.used_ports, 0)) as odp_available_port
                FROM coverage c
                JOIN m_odc odc ON c.coverage_id = odc.coverage_odc
                JOIN m_odp odp ON odc.id_odc = odp.code_odc
                LEFT JOIN (
                    SELECT 
                        id_odp, 
                        COUNT(*) as used_ports
                    FROM customer 
                    GROUP BY id_odp
                ) customer_count ON odp.id_odp = customer_count.id_odp
                WHERE c.coverage_id = %s
                ORDER BY odc.code_odc, odp.code_odp
                """
                cursor.execute(sql, (coverage_id,))
                result = cursor.fetchall()
                logger.info(f"Retrieved {len(result)} records for coverage_id: {coverage_id}")
                return result
        except pymysql.Error as e:
            logger.error(f"MySQL error in get_location_data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in get_location_data: {e}")
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    logger.error(f"Error closing connection in get_location_data: {e}")
    
    def get_odps_by_coverage(self, coverage_id):
        """Get ODPs with customers for customer lookup"""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                sql = """
                SELECT 
                    odp.id_odp,
                    odp.code_odp,
                    odc.code_odc,
                    c.c_name,
                    odp.total_port,
                    COUNT(cust.customer_id) as customer_count
                FROM coverage c
                JOIN m_odc odc ON c.coverage_id = odc.coverage_odc
                JOIN m_odp odp ON odc.id_odc = odp.code_odc
                LEFT JOIN customer cust ON odp.id_odp = cust.id_odp
                WHERE c.coverage_id = %s
                GROUP BY odp.id_odp, odp.code_odp, odc.code_odc, c.c_name, odp.total_port
                HAVING customer_count > 0
                ORDER BY odc.code_odc, odp.code_odp
                """
                cursor.execute(sql, (coverage_id,))
                result = cursor.fetchall()
                logger.info(f"Retrieved {len(result)} ODPs with customers for coverage_id: {coverage_id}")
                return result
        except pymysql.Error as e:
            logger.error(f"MySQL error in get_odps_by_coverage: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in get_odps_by_coverage: {e}")
            return []
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    logger.error(f"Error closing connection in get_odps_by_coverage: {e}")
    
    def get_customers_by_odp(self, id_odp):
        """Get customers connected to specific ODP"""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                sql = """
                SELECT 
                    c.name,
                    c.address,
                    c.no_port_odp,
                    odp.code_odp,
                    odc.code_odc,
                    cov.c_name
                FROM customer c
                JOIN m_odp odp ON c.id_odp = odp.id_odp
                JOIN m_odc odc ON c.id_odc = odc.id_odc
                JOIN coverage cov ON odc.coverage_odc = cov.coverage_id
                WHERE c.id_odp = %s 
                ORDER BY c.no_port_odp
                """
                cursor.execute(sql, (id_odp,))
                result = cursor.fetchall()
                logger.info(f"Retrieved {len(result)} customers for id_odp: {id_odp}")
                return result
        except pymysql.Error as e:
            logger.error(f"MySQL error in get_customers_by_odp: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in get_customers_by_odp: {e}")
            return []
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    logger.error(f"Error closing connection in get_customers_by_odp: {e}")

    def search_customers_by_name(self, customer_name):
        """Search customers by name (partial match)"""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                sql = """
                SELECT 
                    c.name,
                    c.address,
                    c.no_port_odp,
                    c.no_wa,
                    odp.code_odp,
                    odc.code_odc,
                    cov.c_name
                FROM customer c
                JOIN m_odp odp ON c.id_odp = odp.id_odp
                JOIN m_odc odc ON c.id_odc = odc.id_odc
                JOIN coverage cov ON odc.coverage_odc = cov.coverage_id
                WHERE c.name LIKE %s 
                ORDER BY c.name
                LIMIT 20
                """
                search_term = f"%{customer_name}%"
                cursor.execute(sql, (search_term,))
                result = cursor.fetchall()
                logger.info(f"Found {len(result)} customers matching '{customer_name}'")
                return result
        except pymysql.Error as e:
            logger.error(f"MySQL error in search_customers_by_name: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in search_customers_by_name: {e}")
            return []
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    logger.error(f"Error closing connection in search_customers_by_name: {e}")
   

# Create global database manager instance
db_manager = DatabaseManager()