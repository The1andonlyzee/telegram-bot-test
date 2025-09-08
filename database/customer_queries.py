import pymysql
import logging
from database.shared_queries import SharedQueries


logger = logging.getLogger(__name__)

class CustomerQueries(SharedQueries):
    """Database queries related to customer management"""

    def search_customers_by_name(self, customer_name):
        """Search customers by name (partial match)"""
        try:
            sql = """
            SELECT 
                c.name,
                c.address,
                c.no_port_odp,
                c.no_wa,
                odp.code_odp,
                odc.code_odc,
                cov.c_name,
                odp.latitude as odp_latitude,  
                odp.longitude as odp_longitude 
            FROM customer c
            JOIN m_odp odp ON c.id_odp = odp.id_odp
            JOIN m_odc odc ON c.id_odc = odc.id_odc
            JOIN coverage cov ON odc.coverage_odc = cov.coverage_id
            WHERE c.name LIKE %s 
            ORDER BY c.name
            LIMIT 20
            """
            search_term = f"%{customer_name}%"
            result = self.execute_query(sql, (search_term,))
            logger.info(f"Found {len(result)} customers matching '{customer_name}'")
            return result
        except pymysql.Error as e:
            logger.error(f"MySQL error in search_customers_by_name: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in search_customers_by_name: {e}")
            return []
    
    def get_odps_by_coverage(self, coverage_id):
        """Get ODPs with customers for customer lookup"""
        try:
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
            result = self.execute_query(sql, (coverage_id,))
            logger.info(f"Retrieved {len(result)} ODPs with customers for coverage_id: {coverage_id}")
            return result
        except pymysql.Error as e:
            logger.error(f"MySQL error in get_odps_by_coverage: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in get_odps_by_coverage: {e}")
            return []
    
    def get_customers_by_odp(self, id_odp):
        """Get customers connected to specific ODP"""
        try:
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
            result = self.execute_query(sql, (id_odp,))
            logger.info(f"Retrieved {len(result)} customers for id_odp: {id_odp}")
            return result
        except pymysql.Error as e:
            logger.error(f"Error in get_customers_by_odp: {e}")
            return []

customer_db = CustomerQueries()