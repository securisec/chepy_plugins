from typing import TypeVar

import chepy.core

Chepy_SQLiteT = TypeVar("Chepy_SQLiteT", bound="Chepy_SQLite")

class Chepy_SQLite(chepy.core.ChepyCore):
    def sqlite_get_tables(self: Chepy_SQLiteT) -> Chepy_SQLiteT: ...
    def sqlite_get_columns(self: Chepy_SQLiteT, table: str) -> Chepy_SQLiteT: ...
    def sqlite_dump_table(self: Chepy_SQLiteT, table: str) -> Chepy_SQLiteT: ...
    def sqlite_query(self: Chepy_SQLiteT, query: str) -> Chepy_SQLiteT: ...