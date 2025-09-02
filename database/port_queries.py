import pymysql
import logging
from database.base_db import BaseDatabase

logger = logging.getLogger(__name__)

class PortQueries(BaseDatabase):
    """Database queries related to port availability and ODC/ODP management"""
    
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

# Create global port database instance
port_db = PortQueries()