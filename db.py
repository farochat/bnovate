import logging

import pandas as pd
import psycopg2 as pg
import psycopg2.extras
import psycopg2.sql as pg_sql
import yaml


logging.basicConfig(level="INFO")

with open("config.yaml", "r") as config_file:
    DB_CONFIG = yaml.safe_load(config_file)


def _connection_params():
    try:
        db_config = DB_CONFIG["bnovate"]
    except KeyError:
        raise ValueError("DB backend 'bnovate' not defined in config file")

    params = {
        "user": db_config["user"],
        "database": db_config.get("database", db_config["user"]),
        "password": db_config["password"],
        "host": db_config["host"],
        "port": db_config.get("port", 5432),
    }

    return params


def connection():
    """Connect to database."""
    return pg.connect(**_connection_params())


def initialize_db():
    """Initializes the database and tables if they do not exist."""
    db_config = DB_CONFIG["bnovate"]
    con = pg.connect(
        database="postgres",
        user=db_config["user"],
        password=db_config["password"],
        host=db_config["host"],
        port=db_config["port"],
    )

    # Important to allow database creation
    con.autocommit = True
    db_name = db_config["database"]
    with con.cursor() as cur:
        cur.execute(f"SELECT 1 FROM pg_database where datname = '{db_name}'")
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {db_name}")
            logging.info(f"Created DB {db_name}.")

    # Connect to new database
    with connection() as con:
        # Create tables if they do not exist yet
        with con.cursor() as cur:
            # User table (only pkey)
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL
                );
            """
            )
            # Polygon table table (only pkey)
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS polygons (
                    id SERIAL PRIMARY KEY
                );
            """
            )

            # Vertices table enforing unicity on (x, y) pairs
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS vertices (
                    id SERIAL PRIMARY KEY,
                    x FLOAT NOT NULL,
                    y FLOAT NOT NULL,
                    UNIQUE(x, y)
                );
            """
            )

            # Polygon_vertices mapping table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS polygon_vertices (
                    polygon_id INTEGER REFERENCES polygons(id) ON DELETE CASCADE,
                    vertex_id INTEGER REFERENCES vertices(id) ON DELETE CASCADE,
                    PRIMARY KEY (polygon_id, vertex_id)
                );
            """
            )

            # User_polygons mapping table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS user_polygons (
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    polygon_id INTEGER REFERENCES polygons(id) ON DELETE CASCADE,
                    PRIMARY KEY (user_id, polygon_id)
                );
            """
            )

            # Add some indexes for good measure
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_vertices_xy ON vertices (x, y);"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_polygon_vertices ON polygon_vertices (polygon_id, vertex_id);"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_user_polygons ON user_polygons (user_id, polygon_id);"
            )

            logging.info("Database initialized successfully.")


def insert(username, vertices):
    """
    Inserts a polygon for a given user. Ensures no duplicate vertices.
    If a polygon with the same set of vertices exists, links the user to it.
    Otherwise, creates a new polygon entry.

    :param user_id: The ID of the user.
    :param vertices: A list of (x, y) tuples representing the polygon.
    """
    with connection() as con:
        with con.cursor() as cur:
            # Insert user if not yet present
            cur.execute("SELECT id FROM users WHERE username = %s;", (username,))
            user_id = cur.fetchone()
            if not user_id:
                cur.execute(
                    "INSERT INTO users (username) VALUES (%s) RETURNING id;",
                    (username,),
                )
                user_id = cur.fetchone()
            user_id = user_id[0]
            # Insert vertices and get IDs
            vertex_ids = []
            for x, y in vertices:
                cur.execute(
                    "INSERT INTO vertices (x, y) VALUES (%s, %s) ON CONFLICT (x, y) DO NOTHING RETURNING id;",
                    (x, y),
                )
                vertex_id = cur.fetchone()

                # Fetch existing ID if already in table
                if vertex_id is None:
                    cur.execute(
                        "SELECT id FROM vertices WHERE x = %s AND y = %s;", (x, y)
                    )
                    vertex_id = cur.fetchone()

                vertex_ids.append(vertex_id[0])

            # Check if the same set of vertices is already present
            cur.execute(
                """
                SELECT polygon_id
                FROM polygon_vertices
                GROUP BY polygon_id
                HAVING ARRAY_AGG(vertex_id ORDER BY vertex_id) = %s;
            """,
                (sorted(vertex_ids),),
            )

            existing_polygon = cur.fetchone()
            if existing_polygon:
                polygon_id = existing_polygon[0]
            else:
                # Insert new polygon
                cur.execute("INSERT INTO polygons DEFAULT VALUES RETURNING id;")
                polygon_id = cur.fetchone()[0]

                # Insert into polygon_vertices mapping
                for vertex_id in vertex_ids:
                    cur.execute(
                        "INSERT INTO polygon_vertices (polygon_id, vertex_id) VALUES (%s, %s);",
                        (polygon_id, vertex_id),
                    )

            # Assign polygon to user
            cur.execute(
                "INSERT INTO user_polygons (user_id, polygon_id) VALUES (%s, %s);",
                (user_id, polygon_id),
            )

            logging.info(
                f"Polygon inserted for user {user_id}, polygon ID {polygon_id}"
            )


def vertex_from_username(username):
    with connection() as con:
        with con.cursor() as cur:
            try:
                cur.execute("SELECT id FROM users WHERE username = %s", (username,))
                user = cur.fetchone()
                if not user:
                    return None
                user_id = user[0]

                # Fetch the vertices for the user's polygon (assuming one polygon per user)
                cur.execute(
                    """
                    SELECT v.x, v.y
                    FROM vertices v
                    JOIN polygon_vertices pv ON v.id = pv.vertex_id
                    JOIN user_polygons up ON pv.polygon_id = up.polygon_id
                    WHERE up.user_id = %s
                """,
                    (user_id,),
                )
                vertices = cur.fetchall()
            except Exception as e:
                logging.error(f"Error fetching vertices: {e}")
                vertices = None
            finally:
                return vertices


# Run this manually once to initialize the DB
if __name__ == "__main__":
    initialize_db()
