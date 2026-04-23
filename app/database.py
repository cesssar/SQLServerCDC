import pyodbc
from typing import Any


class Database:
    def __init__(self, server: str, database: str, username: str, password: str, port: int = 1433, driver: str = "ODBC Driver 18 for SQL Server"):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.port = port
        self.driver = driver
        self._connection: pyodbc.Connection | None = None

    def connect(self) -> None:
        connection_string = (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server},{self.port};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password};"
            "TrustServerCertificate=yes;"
        )
        self._connection = pyodbc.connect(connection_string)

    def disconnect(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None

    def fetch(self, query: str, params: tuple = ()) -> list[dict[str, Any]]:
        if not self._connection:
            raise ConnectionError("Not connected. Call connect() first.")
        cursor = self._connection.cursor()
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def execute(self, query: str, params: tuple = ()) -> int:
        if not self._connection:
            raise ConnectionError("Not connected. Call connect() first.")
        cursor = self._connection.cursor()
        cursor.execute(query, params)
        self._connection.commit()
        return cursor.rowcount

    def __enter__(self) -> "Database":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.disconnect()
