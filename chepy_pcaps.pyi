import chepy.core
from typing import Any

scapy: Any

class _Pkt2Dict:
    pkt: Any = ...
    def __init__(self, pkt: Any) -> None: ...
    def to_dict(self): ...

class PcapUSB:
    qwerty_map: Any = ...
    qwerty_modifier: Any = ...
    dvorak: Any = ...
    dvorak_modifier: Any = ...

class Pcap(chepy.core.ChepyCore):
    state: str = ...
    def read_pcap(self): ...
    def pcap_dns_queries(self): ...
    def pcap_http_streams(self): ...
    def pcap_payload(self, layer: str, bpf_filter: str=...) -> Any: ...
    def pcap_payload_offset(self, layer: str, start: int, end: int=..., bpf_filter: str=...) -> Any: ...
    def pcap_to_dict(self, bpf_filter: str=...) -> Any: ...
    def pcap_layer_stats(self, bpf_filter: str=...) -> Any: ...
    def pcap_convos(self, bpf_filter: str=...) -> Any: ...
    def pcap_usb_keyboard(self, layout: str=...) -> Any: ...
