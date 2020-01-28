import logging

from OpenSSL import crypto
from OpenSSL.crypto import _lib, _ffi, X509

try:
    import elftools.elf.elffile as _pyelf
    from elftools.elf.relocation import RelocationSection
except ImportError:
    logging.warning("Could not import pyelftools. Use pip install pyelftools")

import chepy.core


class ELFFile(chepy.core.ChepyCore):
    """This plugin allows Chepy to interface with ELF binaries
    """

    def _elf_object(self):
        """Returns an ELFFile object
        """
        return _pyelf.ELFFile(self._load_as_file())

    @chepy.core.ChepyDecorators.call_stack
    def elf_imports(self):
        """Get imports from an ELF file
        
        Returns:
            ChepyPlugin: The Chepy object. 
        """
        hold = {}
        e = self._elf_object()
        for section in e.iter_sections():
            if isinstance(section, RelocationSection):
                symbol_table = e.get_section(section["sh_link"])
                symbols = []
                for relocation in section.iter_relocations():
                    symbol = symbol_table.get_symbol(relocation["r_info_sym"]).name
                    if symbol:
                        symbols.append(symbol)
                hold[section.name] = symbols

        self.state = hold
        return self
