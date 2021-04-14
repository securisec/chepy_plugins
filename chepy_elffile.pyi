import chepy.core
from chepy.modules.publickey import OpenSSL as OpenSSL
from typing import Any

elffile: Any
relocation: Any

class ELFFile(chepy.core.ChepyCore):
    state: Any = ...
    def elf_imports(self): ...
