import logging
from pathlib import Path

import chepy.core


def _generate_function(d: dict, as_code: bool = True) -> str:
    if as_code:
        run = "c.{}(".format(d["function"])
    else:
        run = "{}(".format(d["function"])
    args: dict = d["args"]
    if len(args) > 0:
        for i, k in enumerate(args.items()):
            run += "{}={}".format(k[0], k[1])
            if i + 1 != len(args):
                run += ", "
    run += ")"
    return run


def _generate_chepy_code(stack) -> str:
    code = ["from chepy import Chepy\n\nc = Chepy(data)\n"]

    for d in stack:
        run = _generate_function(d)
        code.append(run)

    return "\n".join(code)


class Chepy_Report(chepy.core.ChepyCore):
    """Generate an html report representation of the current call stack"""

    def html(self, path: str, as_string: bool = True):  # pragma: no cover
        """Generate and write html report

        Args:
            path (str): The path to write the report
            as_string (str, optional): Return the state as a string. False will encode to hex.
                Defaults to True

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

        r = Reportng(
            "Securisec",
            "Chepy",
            user_css="""
        .navbar{padding: 5;} 
        h1{font-size: large; text-transform: initial; letter-spacing: 0;}
        div.container{padding-top:20 !important; padding-bottom:0 !important;}
        span.bar{background-color: #A4BD00 !important;}
        span.text-secondary{color: #A4BD00 !important;}
        """,
        )
        current_stack = self._stack.copy()
        current_state = self.state
        self.states = self._initial_states

        r.code(
            "Chepy Python code", _generate_chepy_code(current_stack), is_section=False
        )

        for recipe in current_stack:
            function = recipe["function"]
            args = recipe["args"]
            if len(args) > 0:
                getattr(self, function)(**args)
                r.section(
                    _generate_function(recipe, False),
                    self.out_as_str() if as_string else self.state,
                )
            else:
                getattr(self, function)()
                r.section(
                    _generate_function(recipe, False),
                    self.out_as_str() if as_string else self.state,
                )

        p = str(Path(path).absolute())
        r.save(path=p)
        logging.info("Saved report to {}".format(p))
        self.state = current_state
        self._stack = current_stack
        return self
