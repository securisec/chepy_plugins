import chepy.core
from typing import Any

RepositoryMining: Any
InvalidGitRepositoryError: Any

class Chepy_Git(chepy.core.ChepyCore):
    state: Any = ...
    def git_search_code(self, search: str, show_errors: bool=...) -> Any: ...
    def git_authors(self, show_errors: bool=...) -> Any: ...
