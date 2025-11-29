# """
# Database Connection Module
# ===========================
# Handles PostgreSQL + PostGIS database connections using SQLAlchemy.
# Provides connection pooling, session management, and connection testing.
# """

# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker, scoped_session
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.pool import QueuePool
# import config

# # Create the SQLAlchemy engine with connection pooling
# engine = create_engine(
#     config.DATABASE_URI,
#     poolclass=QueuePool,
#     pool_size=config.SQLALCHEMY_POOL_SIZE,
#     max_overflow=config.SQLALCHEMY_MAX_OVERFLOW,
#     pool_pre_ping=True,  # Enable connection health checks
#     echo=config.DEBUG  # Log SQL queries in debug mode
# )

# # Create a configured "Session" class
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Create a scoped session for thread-safe operations
# db_session = scoped_session(SessionLocal)

# # Base class for declarative models
# Base = declarative_base()


# def init_db():
#     """
#     Initialize the database connection and create tables if needed.
#     This should be called when the application starts.
#     """
#     try:
#         # Test the connection
#         with engine.connect() as connection:
#             # Check if PostGIS extension is available
#             result = connection.execute(text("SELECT PostGIS_version();"))
#             version = result.fetchone()

#         # TODO: Uncomment to auto-create tables from models
#         # Base.metadata.create_all(bind=engine)

#     except Exception as e:
#         raise


# def get_db():
#     """
#     Get a database session for use in API endpoints.

#     Yields:
#         Session: SQLAlchemy database session

#     Usage:
#         with get_db() as session:
#             # Use session here
#             pass
#     """
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# def test_connection():
#     """
#     Test the database connection and PostGIS functionality.

#     Returns:
#         bool: True if connection is successful, False otherwise
#     """
#     try:
#         with engine.connect() as connection:
#             # Test basic connection
#             result = connection.execute(text("SELECT 1"))
#             if result.fetchone()[0] != 1:
#                 return False

#             # Test PostGIS extension
#             result = connection.execute(text("""
#                 SELECT EXISTS(
#                     SELECT 1 FROM pg_extension WHERE extname = 'postgis'
#                 )
#             """))
#             postgis_installed = result.fetchone()[0]

#             if not postgis_installed:
#                 return False

#             # Test spatial query
#             result = connection.execute(text("""
#                 SELECT ST_AsText(ST_Point(78.9629, 20.5937));
#             """))
#             point = result.fetchone()[0]

#             return True

#     except Exception as e:
#         return False


# def execute_raw_query(query, params=None):
#     """
#     Execute a raw SQL query with optional parameters.

#     Args:
#         query (str): SQL query to execute
#         params (dict, optional): Query parameters

#     Returns:
#         list: Query results as list of dictionaries
#     """
#     try:
#         with engine.connect() as connection:
#             result = connection.execute(text(query), params or {})

#             # Check if query returns results
#             if result.returns_rows:
#                 columns = result.keys()
#                 return [dict(zip(columns, row)) for row in result.fetchall()]
#             else:
#                 connection.commit()
#                 return []

#     except Exception as e:
#         raise


# def close_db():
#     """
#     Close all database connections.
#     Should be called when shutting down the application.
#     """
#     try:
#         db_session.remove()
#         engine.dispose()
#     except Exception as e:
#         pass


# # Cleanup function for Flask teardown
# def teardown_db(exception=None):
#     """
#     Teardown function to remove the database session.
#     Register this with Flask's teardown_appcontext.
#     """
#     db_session.remove()
"""
Database disabled for this project.
Provides safe placeholder values so imports do not break.
"""

engine = None


def init_db():
    print("[INFO] Database disabled — skipping DB initialization.")


def get_db():
    raise RuntimeError("Database disabled. No DB session available.")


def close_db():
    pass
