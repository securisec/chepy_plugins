import logging

try:
    from ua_parser.user_agent_parser import Parse as _uap_parse
except ImportError:
    logging.warning("Could not import ua-parser. Use pip install ua-parser")

import chepy.core


class UserAgent(chepy.core.ChepyCore):
    """This plugin allows Chepy to parse user agent strings
    """

    @chepy.core.ChepyDecorators.call_stack
    def parse_user_agent(self):
        """Parse a User-Agent string.
        
        Attempts to identify and categorise information contained in a user-agent string.
        
        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> ua = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:62.0) Gecko/20100101 Firefox/62.0"
            >>> Chepy(ua).parse_user_agent().o
            {
                "user_agent": {"family": "Firefox", "major": "62", "minor": "0", "patch": None},
                "os": {
                    "family": "Mac OS X",
                    "major": "10",
                    "minor": "10",
                    "patch": None,
                    "patch_minor": None,
                },
                "device": {"family": "Other", "brand": None, "model": None},
                "string": "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:62.0) Gecko/20100101 Firefox/62.0",
            }
        """
        self.state = _uap_parse(self._convert_to_str())
        return self
