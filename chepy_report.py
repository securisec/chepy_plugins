import logging
from pathlib import Path

import chepy.core


class Chepy_Report(chepy.core.ChepyCore):
    """Generate an html report representaion of the current call stack"""

    def html_view(self, path: str):  # pragma: no cover
        """Generate and write html report

        Args:
            path (str): The path to write the report

        Returns:
            ChepyPlugin: The Chepy object.

        Examples:
            >>> # Run other chepy commands in the consome or script
            >>> html_view('/path/to/save.html')
        """
        try:
            from reportng import Reportng
        except ImportError:
            logging.warning("Could not import exiftool. Use pip install exiftool")
            return

        r = Reportng("Chepy", "securisec")
        current_stack = self._stack.copy()
        current_state = self.state
        self.states = self._initial_states

        for recipe in current_stack:
            function = recipe["function"]
            args = recipe["args"]
            if len(args) > 0:
                getattr(self, function)(**args)
                r.section(
                    "{} {}".format(
                        function,
                        " ".join(["--{} {}".format(k, v) for (k, v) in args.items()]),
                    ),
                    self.state,
                )
            else:
                getattr(self, function)()
                r.section("{}".format(function), self.state)

        p = str(Path(path).absolute())
        r.save(path=p)
        logging.info("Saved report to {}".format(p))
        self.state = current_state
        self._stack = current_stack
        return self
