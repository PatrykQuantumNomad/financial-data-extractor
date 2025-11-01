"""
Base repository class providing common database operations.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from typing import Any

from psycopg_pool import AsyncConnectionPool


class BaseRepository:
    """Base repository providing common database operations using async connection pool."""

    def __init__(self, db_pool: AsyncConnectionPool):
        """Initialize repository with database connection pool.

        Args:
            db_pool: Async connection pool for database operations.
        """
        self.db_pool = db_pool

    async def execute_query(
        self, query: str, params: tuple[Any, ...] | dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute a SELECT query and return results as list of dictionaries.

        Args:
            query: SQL query string with placeholders.
            params: Query parameters (tuple for positional, dict for named).

        Returns:
            List of dictionaries representing rows.
        """
        async with self.db_pool.connection() as conn:
            async with conn.cursor() as cur:
                if params:
                    await cur.execute(query, params)
                else:
                    await cur.execute(query)
                rows = await cur.fetchall()
                return list(rows)

    async def execute_one(
        self, query: str, params: tuple[Any, ...] | dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """Execute a SELECT query and return single row as dictionary.

        Args:
            query: SQL query string with placeholders.
            params: Query parameters (tuple for positional, dict for named).

        Returns:
            Dictionary representing a single row, or None if no row found.
        """
        async with self.db_pool.connection() as conn:
            async with conn.cursor() as cur:
                if params:
                    await cur.execute(query, params)
                else:
                    await cur.execute(query)
                row = await cur.fetchone()
                return dict(row) if row else None

    async def execute_insert(
        self,
        query: str,
        params: tuple[Any, ...] | dict[str, Any] | None = None,
        returning: str = "id",
    ) -> Any | None:
        """Execute an INSERT query and return the ID of the inserted row.

        Args:
            query: SQL INSERT query string with placeholders.
            params: Query parameters (tuple for positional, dict for named).
            returning: Column name to return (default: 'id').

        Returns:
            Value of the returned column (typically ID), or None if not found.
        """
        # Check if query already has RETURNING clause
        if "RETURNING" in query.upper():
            query_with_returning = query
        else:
            query_with_returning = f"{query} RETURNING {returning}"

        async with self.db_pool.connection() as conn:
            async with conn.cursor() as cur:
                if params:
                    await cur.execute(query_with_returning, params)
                else:
                    await cur.execute(query_with_returning)
                result = await cur.fetchone()
                if result and returning in result:
                    return result[returning]
                return result if result else None

    async def execute_update(
        self, query: str, params: tuple[Any, ...] | dict[str, Any] | None = None
    ) -> int:
        """Execute an UPDATE query and return number of affected rows.

        Args:
            query: SQL UPDATE query string with placeholders.
            params: Query parameters (tuple for positional, dict for named).

        Returns:
            Number of rows affected.
        """
        async with self.db_pool.connection() as conn:
            async with conn.cursor() as cur:
                if params:
                    await cur.execute(query, params)
                else:
                    await cur.execute(query)
                return cur.rowcount

    async def execute_delete(
        self, query: str, params: tuple[Any, ...] | dict[str, Any] | None = None
    ) -> int:
        """Execute a DELETE query and return number of affected rows.

        Args:
            query: SQL DELETE query string with placeholders.
            params: Query parameters (tuple for positional, dict for named).

        Returns:
            Number of rows affected.
        """
        async with self.db_pool.connection() as conn:
            async with conn.cursor() as cur:
                if params:
                    await cur.execute(query, params)
                else:
                    await cur.execute(query)
                return cur.rowcount
