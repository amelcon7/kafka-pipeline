import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="enterprise_agent",
        user="app",
        password="app",
        cursor_factory=RealDictCursor,
    )
