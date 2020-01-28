import logging

try:
    from markdown import markdown
except ImportError:
    logging.warning("Could not import markdown. Use pip install Markdown")

import chepy.core


class Chepy_Markdown(chepy.core.ChepyCore):
    """This plugin allows converting markdown to html
    """

    @chepy.core.ChepyDecorators.call_stack
    def markdown_to_html(self):
        """Convert markdown syntax to html
        
        Returns:
            ChepyPlugin: The Chepy object. 
        """
        self.state = markdown(self._convert_to_str())
        return self
