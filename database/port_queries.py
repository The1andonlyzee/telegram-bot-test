import pymysql
import logging
from database.base_db import BaseDatabase
from database.shared_queries import shared_db
from database.shared_queries import SharedQueries


logger = logging.getLogger(__name__)

class PortQueries(SharedQueries):
    """Database queries related to port availability and ODC/ODP management"""
    
    
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
                    odc.latitude as odc_latitude,
                    odc.longitude as odc_longitude,
                    odp.code_odp,
                    odp.latitude as odp_latitude,
                    odp.longitude as odp_longitude,
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
                result = self.execute_query(sql, (coverage_id,))
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

# Create global port database instance
port_db = PortQueries()