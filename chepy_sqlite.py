import logging
from pathlib import Path

# TODO move sql import to lazy
import sqlite3

import chepy.core


class Chepy_SQLite(chepy.core.ChepyCore):
    """This plugin allows interacting with SQLite3 database files"""

    def _conn(self):
        p = Path(self._convert_to_str())
        if not p.is_file():
            logging.error("State is not a valid file path")
        return sqlite3.connect(f"file:{str(p)}?mode=rw", uri=True)

    @chepy.core.ChepyDecorators.call_stack
    def sqlite_get_tables(self):
        """Get all table names from db

        Returns:
            ChepyPlugin: The Chepy object.
        """
        curr = self._conn().execute('select name from sqlite_master where type="table"')
        self.state = [c for [c] in curr]
        return self

    @chepy.core.ChepyDecorators.call_stack
    def sqlite_get_columns(self, table: str):
        """List all columns of a table

        Args:
            table (str): A valid table name

        Returns:
            ChepyPlugin: The Chepy object.
        """
        curr = self._conn().execute(f"select * from {table};")
        self.state = [c[0] for c in curr.description]
        return self

    @chepy.core.ChepyDecorators.call_stack
    def sqlite_dump_table(self, table: str):
        """Dump all data from a table

        Args:
            table (str): A valid table name

        Returns:
            ChepyPlugin: The Chepy object.
        """
        curr = self._conn().execute(f"select * from {table};")
        self.state = [c for c in curr]
        return self

    @chepy.core.ChepyDecorators.call_stack
    def sqlite_query(self, query: str):
        """Run a raw sql query

        Args:
            query (str): The sql query string

        Returns:
            ChepyPlugin: The Chepy object.
        """
        curr = self._conn().execute(query)
        self.state = [c for c in curr]
        return self