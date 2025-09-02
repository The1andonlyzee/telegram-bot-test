import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

try:
    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASS"),
        db=os.getenv("MYSQL_DB"),
        cursorclass=pymysql.cursors.DictCursor
    )
    print("✅ Database connection successful!")
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as count FROM m_odc")
        result = cursor.fetchone()
        print(f"✅ Found {result['count']} records in m_odc")
        
except Exception as e:
    print(f"❌ Database connection failed: {e}")
finally:
    if 'conn' in locals():
        conn.close()