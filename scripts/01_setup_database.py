import psycopg2
import logging
import os

# --- Configuration ---
DB_NAME = "hockey_analytics"
DB_USER = "hockey_user"
DB_PASS = "strongpassword"
DB_HOST = "odysseus_db" # Use the service name as the hostname
DB_PORT = "5432"

LOG_FILE = "logs/01_setup_database.log"

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def create_tables():
    """Create tables in the PostgreSQL database."""
    commands = (
        """
        CREATE TABLE IF NOT EXISTS videos (
            video_id SERIAL PRIMARY KEY,
            source_url VARCHAR(512) UNIQUE NOT NULL,
            title VARCHAR(255),
            local_path VARCHAR(512) NOT NULL,
            download_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            processed_status VARCHAR(20) NOT NULL DEFAULT 'unprocessed'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS video_clips (
            clip_id SERIAL PRIMARY KEY,
            parent_video_id INTEGER NOT NULL REFERENCES videos(video_id),
            local_path VARCHAR(512) NOT NULL,
            start_time_sec FLOAT,
            end_time_sec FLOAT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS keyframes (
            frame_id SERIAL PRIMARY KEY,
            parent_video_id INTEGER NOT NULL REFERENCES videos(video_id),
            local_path VARCHAR(512) NOT NULL,
            timestamp_sec FLOAT
        )
        """
    )
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        cur.close()
        conn.commit()
        logging.info("Tables created successfully or already exist.")
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    # Ensure the logs directory exists before writing to it
    log_dir = os.path.dirname(LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    create_tables()
