import logging
import pkg_resources

try:
    import regex
except ImportError:
    logging.warning("Could not import regex. Use pip install regex")

import chepy.core


class Chepy_Extract(chepy.core.ChepyCore):
    """Chepy plugin that handles extended secrets and extract operations
    """

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
        found = {}
        secrets_path = pkg_resources.resource_filename(__name__, "data/secrets.txt")
        with open(secrets_path, "r") as f:
            for pattern in f:
                matches = regex.findall(pattern.strip(), self._convert_to_str())
                if matches:
                    found[regex.sub(r"[^a-zA-Z0-9_]", "", pattern[0:20])] = matches
        self.state = found
        return self
