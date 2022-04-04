import logging
import json
import phpserialize
from lxml import etree
import lazy_import

try:
    import regex

    jsonpath_rw = lazy_import.lazy_module("jsonpath_rw")
    parsel = lazy_import.lazy_module("parsel")
except ImportError:
    logging.warning("Could not import regex. Use pip install regex")

import chepy.core


class Chepy_Extract(chepy.core.ChepyCore):
    """Chepy plugin that handles extended secrets and extract operations"""

    def _parsel_obj(self):
        """Returns a parsel.Selector object"""
        return parsel.Selector(self._convert_to_str())

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

    @chepy.core.ChepyDecorators.call_stack
    def xpath_selector(self, query: str, namespaces: str = None):
        """Extract data using valid xpath selectors

        Args:
            query (str): Required. Xpath query
            namespaces (str, optional): Namespace. Applies for XML data. Defaults to None.

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> c = Chepy("http://example.com")
            >>> c.http_request()
            >>> c.xpath_selector("//title/text()")
            >>> c.get_by_index(0)
            >>> c.o
            "Example Domain"
        """
        self.state = (
            parsel.Selector(self._convert_to_str(), namespaces=namespaces)
            .xpath(query)
            .getall()
        )
        return self

    @chepy.core.ChepyDecorators.call_stack
    def css_selector(self, query: str):
        """Extract data using valid CSS selectors

        Args:
            query (str): Required. CSS query

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> c = Chepy("http://example.com")
            >>> c.http_request()
            >>> c.css_selector("title")
            >>> c.get_by_index(0)
            >>> c.o
            "<title>Example Domain</title>"
        """
        self.state = self._parsel_obj().css(query).getall()
        return self

    @chepy.core.ChepyDecorators.call_stack
    def php_deserialize(self):
        """Deserialize php to dict

        Deserializes PHP serialized data, outputting keyed arrays as a python dict.

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> c = Chepy('a:3:{i:1;s:6:"elem 1";i:2;s:6:"elem 2";i:3;s:7:" elem 3";}')
            >>> c.php_deserialize()
            {1: b'elem 1', 2: b'elem 2', 3: b' elem 3'}
        """
        self.state = phpserialize.loads(self._convert_to_bytes())
        return self

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

    @chepy.core.ChepyDecorators.call_stack
    def html_tags(self, tag: str):
        """Extract tags from html along with their attributes

        Args:
            tag (str): A HTML tag

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("http://example.com").http_request().html_tags('p').o
            [
                {'tag': 'p', 'attributes': {}},
                {'tag': 'p', 'attributes': {}},
                {'tag': 'p', 'attributes': {}}
            ]
        """
        tags = []

        for element in self._parsel_obj().xpath("//{}".format(tag)):
            attributes = []
            for index, attribute in enumerate(element.xpath("@*"), start=1):
                attribute_name = element.xpath("name(@*[%d])" % index).extract_first()
                attributes.append((attribute_name, attribute.extract()))
            tags.append({"tag": tag, "attributes": dict(attributes)})

        self.state = tags
        return self

    @chepy.core.ChepyDecorators.call_stack
    def html_comments(self):
        """Extract html comments

        Returns:
            Chepy: The Chepy object.
        """
        self.state = list(
            filter(lambda x: x != "", self._parsel_obj().xpath("//comment()").getall())
        )
        return self
