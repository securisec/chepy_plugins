import logging
import tempfile
import chepy.core

try:
    from PIL import Image
    from pyzbar import pyzbar
    import zxing
except ImportError:
    logging.error("Could not import PIL, zxing or pyzbar")


class Chepy_QR(chepy.core.ChepyCore):
    pass

    @chepy.core.ChepyDecorators.call_stack
    def qr_decode(self, show_all: bool = False):  # pragma: no cover
        """Decode a qr code. This method does require zbar to be installed in the system

        Args:
            show_all: If true, show all decoded data. If false, show only the first decoded data.

        Returns:
            ChepyPlugin: The Chepy object.
        """
        data = Image.open(self._load_as_file())
        texts = list(map(lambda x: x.data, pyzbar.decode(data)))
        if len(texts) == 0:
            logging.error("Could not decode QR code")
        else:
            if show_all:
                self.state = texts
            else:
                self.state = texts[0]
        return self

    @chepy.core.ChepyDecorators.call_stack
    def qr_decode_other(self):
        """Decode a qr code

        This method does require zxing to be installed. For this method to work,
        it creates a temporary file and then deletes it.

        Returns:
            ChepyPlugin: The Chepy object.
        """
        formats = {"PNG": "png", "JPEG": "jpg", "GIF": "gif"}
        data = Image.open(self._load_as_file())
        fmat = formats.get(data.format)
        if fmat is None:
            logging.error("Could not decode QR code")
            return self
        # create temp file
        with tempfile.NamedTemporaryFile(delete=True, suffix=".{}".format(fmat)) as tf:
            data.save(tf)
            # tf.write(data.tobytes())
            reader = zxing.BarCodeReader()
            result = reader.decode(tf.name)
            if result is None:
                logging.error("Could not decode QR code")
            else:
                self.state = result.parsed
        return self

    # @chepy.core.ChepyDecorators.call_stack
    # def qr_to_ascii(self):
    #     """
    #     Convert a qr code to ascii

    #     Returns:
    #         ChepyPlugin: The Chepy object.
    #     """
    #     # TODO: Implement this
    #     logging.warning("Not implemented yet")
    #     pass
