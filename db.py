from sqlalchemy import create_engine
from sqlalchemy.engine import URL

connection_url = URL.create(
    "mysql+pymysql",
    username="root",
    password="maiden1821SK!@#",
    host="localhost",
    port=3306,
    database="mrp_db"
)

engine = create_engine(connection_url)