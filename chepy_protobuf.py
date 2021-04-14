import logging

try:
    import blackboxprotobuf
except ImportError:
    logging.warning(
        "Could not import blackboxprotobuf. Use pip install blackboxprotobuf"
    )

import chepy.core


class Chepy_Protobuf(chepy.core.ChepyCore):
    """This plugin allows helps decoding protobuf without
    proto file
    """

    @chepy.core.ChepyDecorators.call_stack
    def protobuf_decode_json(self, bytes_as_hex: bool = False):
        """Decode protobuf to json string

        Args:
            bytes_as_hex (bool, optional): Convert bytes to hex. Defaults to False.

        Returns:
            ChepyPlugin: The Chepy object.
        """
        j, _ = blackboxprotobuf.protobuf_to_json(
            self._convert_to_bytes(), bytes_as_hex=bytes_as_hex
        )
        self.state = j
        return self

    @chepy.core.ChepyDecorators.call_stack
    def protobuf_decode_dict(self):
        """Decode protobuf to python dict

        Returns:
            ChepyPlugin: The Chepy object.
        """
        j, _ = blackboxprotobuf.decode_message(self._convert_to_bytes())
        self.state = j
        return self
