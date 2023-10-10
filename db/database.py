import sqlite3

class Database:

    def __init__(self, dbfile: str):
        self._conn = sqlite3.connect(dbfile)
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def connection(self) -> sqlite3.Connection:
        return self._conn

    @property
    def cursor(self) -> sqlite3.Cursor:
        return self._cursor

    def commit(self) -> None:
        self.connection.commit()

    def close(self, commit=True) -> None:
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=()) -> None:
        self.cursor.execute(sql, params)

    def fetchone(self) -> tuple:
        return self.cursor.fetchone()

    def fetchall(self) -> list[tuple]:
        return self.cursor.fetchall()