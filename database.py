import logging
import psycopg2
import psycopg2.extras
from pgvector.psycopg2 import register_vector
from config import DB_CONFIG
from datetime import datetime
import numpy as np

logger = logging.getLogger("database")

class PgVectorDB:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            register_vector(self.conn)
            self.ensure_tables()
            logger.info("Database connection established.")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def ensure_tables(self):
        """Create required tables if they do not exist."""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    CREATE EXTENSION IF NOT EXISTS vector;
                    CREATE TABLE IF NOT EXISTS employees (
                        id VARCHAR PRIMARY KEY,
                        name VARCHAR NOT NULL,
                        embedding vector(128),
                        registered_date TIMESTAMP,
                        num_samples INTEGER,
                        model VARCHAR,
                        image BYTEA
                    );
                    CREATE TABLE IF NOT EXISTS employee_faces (
                        id SERIAL PRIMARY KEY,
                        employee_id VARCHAR REFERENCES employees(id),
                        pose VARCHAR,
                        embedding vector(128),
                        image BYTEA,
                        captured_at TIMESTAMP
                    );
                    CREATE TABLE IF NOT EXISTS attendance (
                        id SERIAL PRIMARY KEY,
                        employee_id VARCHAR,
                        name VARCHAR,
                        timestamp TIMESTAMP
                    );
                """)
                self.conn.commit()
            logger.info("Tables ensured/created.")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            self.conn.rollback()
            raise

    def upsert_employee(self, employee_id, name, embedding, registered_date, num_samples, model, image_bytes):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO employees (id, name, embedding, registered_date, num_samples, model, image)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    embedding = EXCLUDED.embedding,
                    registered_date = EXCLUDED.registered_date,
                    num_samples = EXCLUDED.num_samples,
                    model = EXCLUDED.model,
                    image = EXCLUDED.image
            """, (employee_id, name, embedding.tolist(), registered_date, num_samples, model, image_bytes))
            self.conn.commit()

    def insert_employee_face(self, employee_id, pose, embedding, image_bytes, captured_at):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO employee_faces (employee_id, pose, embedding, image, captured_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (employee_id, pose, embedding.tolist(), image_bytes, captured_at))
            self.conn.commit()

    def fetch_all_employees(self):
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM employees")
            return cur.fetchall()
    
    def fetch_employee_by_id(self, employee_id):
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM employees WHERE id=%s", (employee_id,))
            return cur.fetchone()
    
    def fetch_faces_by_employee(self, employee_id):
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM employee_faces WHERE employee_id=%s", (employee_id,))
            return cur.fetchall()

    def delete_employee(self, employee_id):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM employee_faces WHERE employee_id=%s", (employee_id,))
            cur.execute("DELETE FROM employees WHERE id=%s", (employee_id,))
            self.conn.commit()

    def pgvector_search(self, embedding, top_k=1):
        # Ensure embedding is np.float32 or np.float64
        embedding = np.asarray(embedding, dtype=np.float32)
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
                SELECT id, name, embedding, 1 - (embedding <=> %s) as similarity
                FROM employees
                ORDER BY embedding <=> %s
                LIMIT %s
            """, (embedding, embedding, top_k))
            return cur.fetchall()
        
        
    def record_attendance(self, employee_id, name):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO attendance (employee_id, name, timestamp) VALUES (%s, %s, %s)",
                (employee_id, name, datetime.now())
            )
            self.conn.commit()

