import chepy.core
from typing import Any

class Chepy_Report(chepy.core.ChepyCore):
    states: Any = ...
    state: Any = ...
    def html(self, path: str) -> Any: ...
