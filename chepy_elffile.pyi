import chepy.core
from typing import Any

elffile: Any
relocation: Any

class Chepy_ELFFile(chepy.core.ChepyCore):
    state: Any = ...
    def elf_imports(self): ...
