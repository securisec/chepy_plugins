import chepy.core
from OpenSSL import crypto as crypto
from OpenSSL.crypto import X509 as X509
from typing import Any

class ELFFile(chepy.core.ChepyCore):
    state: Any = ...
    def elf_imports(self): ...
