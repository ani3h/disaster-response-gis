"""
Database Tests
==============
Tests for database connection and queries.
"""

import pytest
from backend.db.db_connection import test_connection, execute_raw_query


def test_database_connection():
    """Test database connection"""
    result = test_connection()
    assert result is True


def test_postgis_extension():
    """Test PostGIS extension is available"""
    query = "SELECT PostGIS_version();"

    try:
        result = execute_raw_query(query)
        assert len(result) > 0
    except Exception as e:
        pytest.fail(f"PostGIS extension not available: {e}")


def test_query_hospitals():
    """Test querying hospitals table"""
    query = "SELECT COUNT(*) as count FROM hospitals;"

    try:
        result = execute_raw_query(query)
        assert 'count' in result[0]
        assert result[0]['count'] >= 0
    except Exception as e:
        pytest.skip(f"Hospitals table not available: {e}")


def test_query_shelters():
    """Test querying shelters table"""
    query = "SELECT COUNT(*) as count FROM shelters;"

    try:
        result = execute_raw_query(query)
        assert 'count' in result[0]
        assert result[0]['count'] >= 0
    except Exception as e:
        pytest.skip(f"Shelters table not available: {e}")


# TODO: Add more database tests
# - Test spatial queries
# - Test data insertion
# - Test data updates
# - Test constraints and indexes
