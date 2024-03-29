import logging
import json
from lxml import etree
import lazy_import

try:
    import regex

    jsonpath_rw = lazy_import.lazy_module("jsonpath_rw")
except ImportError:
    logging.warning("Could not import regex. Use pip install regex")

import chepy.core


class Chepy_Extract(chepy.core.ChepyCore):
    """Chepy plugin that handles extended secrets and extract operations"""

    @chepy.core.ChepyDecorators.call_stack
    def extract_common_secrets(self, case_insensitive: bool = True):
        """Checks for secrets

        Checks ~1000 different secrets patterns. Returns a dict of partial
        pattern name as the key, and and array of found matches as the value.
        This mostly checks for common variable names that contains secrets.

        Args:
            case_insensitive (bool, optional): Case insensitive search. Defaults to True

        Returns:
            ChepyPlugin: The Chepy object.
        """
        # Increase load speed
        import pkg_resources

        found = {}
        secrets_path = pkg_resources.resource_filename(__name__, "data/secrets.txt")
        with open(secrets_path, "r") as f:
            for pattern in f:
                matches = regex.findall(pattern.strip(), self._convert_to_str())
                if matches:
                    found[regex.sub(r"[^a-zA-Z0-9_]", "", pattern[0:20])] = matches
        self.state = found
        return self

    @chepy.core.ChepyDecorators.call_stack
    def jpath_selector(self, query: str):
        """Query JSON with jpath query

        `Reference <https://goessner.net/articles/JsonPath/index.html#e2>`__

        Args:
            query (str): Required. Query. For reference, see the help

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> c = Chepy("tests/files/test.json")
            >>> c.load_file()
            >>> c.jpath_selector("[*].name.first")
            >>> c.get_by_index(2)
            >>> c.o
            "Long"
        """
        self.state = list(
            j.value
            for j in jsonpath_rw.parse(query).find(json.loads(self._convert_to_str()))
        )
        return self

    # @chepy.core.ChepyDecorators.call_stack
    # def php_deserialize(self):
    #     """Deserialize php to dict

    #     Deserializes PHP serialized data, outputting keyed arrays as a python dict.

    #     Returns:
    #         Chepy: The Chepy object.

    #     Examples:
    #         >>> c = Chepy('a:3:{i:1;s:6:"elem 1";i:2;s:6:"elem 2";i:3;s:7:" elem 3";}')
    #         >>> c.php_deserialize()
    #         {1: b'elem 1', 2: b'elem 2', 3: b' elem 3'}
    #     """
    #     self.state = phpserialize.loads(self._convert_to_bytes())
    #     return self

    @chepy.core.ChepyDecorators.call_stack
    def minify_xml(self):
        """Minify XML string

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> c = Chepy("/path/to/file.xml").load_file()
            >>> print(c.minify_xml())
        """
        parser = etree.XMLParser(remove_blank_text=True)
        self.state = etree.tostring(
            etree.fromstring(self._convert_to_bytes(), parser=parser)
        )
        return self

    @chepy.core.ChepyDecorators.call_stack
    def beautify_xml(self):
        """Beautify compressed XML

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> c = Chepy("/path/to/file.xml").load_file()
            >>> print(c.beautify_json())
        """
        self.state = etree.tostring(
            etree.fromstring(self._convert_to_bytes()), pretty_print=True
        )
        return self
