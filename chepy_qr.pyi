from typing import TypeVar

import chepy.core

Chepy_QRT = TypeVar("Chepy_QRT", bound="Chepy_QR")

class Chepy_QR(chepy.core.ChepyCore):
    def qr_decode(self: Chepy_QRT, show_all: bool = ...) -> Chepy_QRT: ...
    def qr_to_ascii(self: Chepy_QRT) -> Chepy_QRT: ...
    # def qr_decode_other(self: Chepy_QRT) -> Chepy_QRT: ...
