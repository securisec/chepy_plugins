import lazy_import

hashid = lazy_import.lazy_module("hashid")


import chepy.core


class Hash(chepy.core.ChepyCore):
    """This plugin Chepy hashing functions"""


    @chepy.core.ChepyDecorators.call_stack
    def identify_hash(self):
        """Identify hash type

        Tries to determine information about a given hash and suggests which
        algorithm may have been used to generate it based on its length.

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("6dcd4ce23d88e2ee9568ba546c007c63d9131c1b").identify_hash().o
            [
                {'hashcat': 100, 'john': 'raw-sha1', 'name': 'SHA-1'},
                {'hashcat': 4500, 'john': None, 'name': 'Double SHA-1'},
                {'hashcat': 6000, 'john': 'ripemd-160', 'name': 'RIPEMD-160'},
                {'hashcat': None, 'john': None, 'name': 'Haval-160'},
                ...
            ]
        """
        hashes = []
        for h in hashid.HashID().identifyHash(self._convert_to_str()):
            hashes.append({"name": h.name, "hashcat": h.hashcat, "john": h.john})
        self.state = hashes
        return self