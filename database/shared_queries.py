from database.base_db import BaseDatabase
import logging

logger = logging.getLogger(__name__)

class SharedQueries(BaseDatabase):
    """Shared database queries used across multiple modules"""
    
    def get_all_locations(self):
        """Get all coverage locations - shared implementation"""
        try:
            sql = "SELECT coverage_id, c_name FROM coverage WHERE c_name IS NOT NULL AND c_name != '' ORDER BY c_name"
            results = self.execute_query(sql)
            locations = [(row["coverage_id"], row["c_name"]) for row in results if row["c_name"]]
            logger.info(f"Retrieved {len(locations)} unique locations")
            return locations
        except Exception as e:
            logger.error(f"Error in get_all_locations: {e}")
            return []

# Create global shared instance
shared_db = SharedQueries()