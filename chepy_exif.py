import logging

try:
    import exiftool
except ImportError:
    logging.warning("Could not import exiftool. Use pip install exiftool")

import chepy.core


class Chepy_Exif(chepy.core.ChepyCore):
    """This plugin allows exif data from files and images
    """

    @chepy.core.ChepyDecorators.call_stack
    def get_exif(self):  # pragma: no cover
        """Extract EXIF data from a file
        
        Returns:
            Chepy: The Chepy object. 
        """
        filename = self._temp_file()
        with exiftool.ExifTool() as et:
            exif = et.get_metadata(filename)
            if exif:
                self.state = exif
            else:
                self._warning_logger("No exif data found")
        return self
