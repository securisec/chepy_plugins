import lazy_import
import os
import logging
import pathlib
import tempfile
import logging

try:
    hachoir = lazy_import.lazy_module("hachoir")
    hachoirParser = lazy_import.lazy_module("hachoir.parser")
    hachoirMeta = lazy_import.lazy_module("hachoir.metadata")
    hachoirMetaItem = lazy_import.lazy_module("hachoir.metadata.metadata_item")
    hachoirSubfile = lazy_import.lazy_module("hachoir.subfile.search")
    hachoirStream = lazy_import.lazy_module("hachoir.stream")
    import hachoir.core.config as hachoir_config
except ImportError:
    logging.warning("Could not import hachoir. Use pip install hachoir==3.1.0")

import chepy.core


class Chepy_Forensics(chepy.core.ChepyCore):
    hachoir_config.quiet = True

    def _temp_file(self) -> str:
        """Get a random temporary file. os.urandom is used here
        because of permission issues using tempfile on Windows.
        The state is then saved in this temp file.

        Returns:
            str: cross platform temporary file
        """
        temp_file = str(pathlib.Path(tempfile.gettempdir()) / os.urandom(24).hex())
        with open(temp_file, "wb") as f:
            f.write(self._convert_to_bytes())
        return temp_file

    @chepy.core.ChepyDecorators.call_stack
    def file_magic(self):  # pragma: no cover
        """Get the file magic

        This method does require python-magic or python-magic-bin to be installed.

        Returns:
            ChepyPlugin: The Chepy object.
        """
        try:
            from puremagic import magic_string

            m = magic_string(self._convert_to_bytes())
            self.state = [dict(x._asdict()) for x in m]
            return self
        except ImportError:
            self._error_logger("Could not import magic. Try pip install python-magic")
            return self

    @chepy.core.ChepyDecorators.call_stack
    def get_metadata(self):
        """Get metadata from a file

        Args:
            set_state (bool, optional): Save the output to state. Defaults to False.

        Returns:
            ChepyPlugin: The Chepy object.

        Examples:
            >>> Chepy("logo.png").load_file().get_metadata().o
            {'Bits/pixel': '32',
            'Compression': 'deflate',
            'Compression rate': '138.6x',
            'Creation date': '2019-11-30 21:40:30',
            'Endianness': 'Big endian',
            'Image DPI height': '3780 DPI',
            'Image DPI width': '3780 DPI',
            'Image height': '1080 pixels',
            'Image width': '1920 pixels',
            'MIME type': 'image/png',
            'Pixel format': 'RGBA'}
        """
        filename = self._temp_file()
        filename, realname = filename, filename
        parser = hachoirParser.createParser(filename, realname)
        if not parser:  # pragma: no cover
            logging.warning("Unable to parse file")

        metadata = hachoirMeta.extractMetadata(
            parser, quality=hachoirMetaItem.QUALITY_BEST
        )

        if metadata is not None:
            meta = metadata.exportDictionary()["Metadata"]
            self.state = meta
        return self

    @chepy.core.ChepyDecorators.call_stack
    def embedded_files(self, extract_path: str = None):
        """Search for embedded files and extract them

        This method does not change the state.

        Args:
            extract_path (str, optional): Path to extract files to. Defaults to None.

        Returns:
            ChepyPlugin: The Chepy object.

        Examples:
            >>> Chepy("/tmp/stego_50.jpg").load_file().embedded_files(extract_path="/tmp/embedded")
            [+] Start search on 10757 bytes (10.5 KB)
            [+] End of search -- offset=10757 (10.5 KB)
            [+] File at 0 size=10541 (10.3 KB): JPEG picture: 430x425 pixels => /tmp/embedded/file-0001.jpg
            [+] File at 10541 size=201 (201 bytes): ZIP archive => /tmp/embedded/file-0002.zip
        """
        filename = self._temp_file()
        inp = hachoirStream.FileInputStream(filename)
        subfile = hachoirSubfile.SearchSubfile(inp)
        if extract_path is not None:  # pragma: no cover
            subfile.setOutput(extract_path)
        subfile.loadParsers()
        subfile.main()
        # pathlib.Path(filename).unlink()
        return self
