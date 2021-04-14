import chepy.core
from typing import Any

hachoir: Any
hachoirParser: Any
hachoirMeta: Any
hachoirMetaItem: Any
hachoirSubfile: Any
hachoirStream: Any

class Chepy_Forensics(chepy.core.ChepyCore):
    state: Any = ...
    def file_magic(self): ...
    def get_metadata(self): ...
    def embedded_files(self, extract_path: str=...) -> Any: ...
