from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2 import Error

# Create FastAPI app
app = FastAPI()

# Database connection settings
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5433"
POSTGRES_DB = "simple_bank"
POSTGRES_USER = "root"
POSTGRES_PASSWORD = "password"


# Function to establish a connection to PostgreSQL
def get_db_conn():
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        return conn
    except Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        raise HTTPException(status_code=500, detail="Database error")


# Define your endpoint
@app.get("/data/")
async def get_data():
    try:
        # Establish a connection to the database
        conn = get_db_conn()

        # Create a cursor object
        cur = conn.cursor()

        # Execute your SELECT query
        cur.execute("SELECT * FROM log;")

        # Fetch all rows
        rows = cur.fetchall()

        # Close cursor and connection
        cur.close()
        conn.close()

        return rows
    except Error as e:
        print(f"Error executing query: {e}")
        raise HTTPException(status_code=500, detail="Query execution error")


# Define your endpoint to get filtered data
@app.get("/filtered-data/{column_name}/{value}")
async def get_filtered_data(column_name: str, value: str):
    try:
        # Establish a connection to the database
        conn = get_db_conn()

        # Create a cursor object
        cur = conn.cursor()

        # Execute your SELECT query with filter
        cur.execute(f"SELECT l.id, l.date, l.username,u.email, l.request_body, l.limit_, l.depth_, l.request_rels, l.obwii, l.approvement_data FROM log l join users u on l.username= u.username WHERE l.{column_name} = %s;", (value,))

        # Fetch all rows
        rows = cur.fetchall()

        # Close cursor and connection
        cur.close()
        conn.close()

        return rows
    except Error as e:
        print(f"Error executing query: {e}")
        raise HTTPException(status_code=500, detail="Query execution error")