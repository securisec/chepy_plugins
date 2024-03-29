import logging
from pathlib import Path

import lazy_import
import regex as re

try:
    RepositoryMining = lazy_import.lazy_class("pydriller.Repository")
    InvalidGitRepositoryError = lazy_import.lazy_module(
        "git.exc.InvalidGitRepositoryError"
    )
    logging.getLogger("pydriller").setLevel(logging.WARNING)
except ImportError:
    logging.warning("Could not import pydriller. Use pip install pydriller")

import chepy.core


class Chepy_Git(chepy.core.ChepyCore):
    """This plugin allows searching through git repositories"""

    def _git_instance(self):
        try:
            _git_dir = Path(self._convert_to_str()).expanduser()
            if not _git_dir.is_dir():
                raise TypeError("Not a directory")
            return RepositoryMining(str(_git_dir))
        except InvalidGitRepositoryError:
            self._error_logger("Not a git repository")
            raise

    @chepy.core.ChepyDecorators.call_stack
    def git_search_code(self, search: str, show_errors: bool = False):
        """Search all commits for match

        Args:
            search (str): The regex string to search
            show_errors (bool): Show hashes that errored

        Returns:
            ChepyPlugin: The Chepy object.
        """
        found = {}

        for commit in self._git_instance().traverse_commits():
            try:
                all_matched = []
                for modified_file in commit.modifications:
                    matched = re.findall(search, modified_file.source_code)
                    if len(matched) > 0:
                        all_matched += matched
                if len(all_matched) > 0:
                    found[commit.hash] = {
                        "matched": all_matched,
                        "author": commit.author.name,
                    }
            except:
                if show_errors:
                    self._error_logger(commit.hash)
                else:
                    continue
        self.state = found
        return self

    @chepy.core.ChepyDecorators.call_stack
    def git_authors(self, show_errors: bool = False):
        """Get a dict of authors and commit count

        Args:
            show_errors (bool, optional): Show hashes with errors. Defaults to False.

        Returns:
            ChepyPlugin: The Chepy object.
        """
        found = {}
        for commit in self._git_instance().traverse_commits():
            try:
                author = commit.author.name
                email = commit.author.email
                if found.get(author) is not None:
                    found[author]['count'] = found[author]['count'] + 1
                    if not email in found[author]['emails'] and email is not None:
                        found[author]['emails'].append(email)
                else:
                    found[author] = {'count': 1, 'emails': [email] if email is not None else []}
            except:
                if show_errors:
                    self._error_logger(commit.hash)
                continue
        self.state = found
        return self
