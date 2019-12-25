import sys
import binascii
import collections

import regex as re
import logging

try:
    import scapy.all as scapy
    import scapy.layers.http as scapy_http
except ImportError:
    logging.warning("Could not import scapy. Use pip install scapy")

import chepy.core


def _full_duplex(p):  # pragma: no cover
    """Create a full duplex stream from packets
    `Reference <https://gist.github.com/MarkBaggett/d8933453f431c111169158ce7f4e2222>`__
    """
    sess = "Other"
    if "Ether" in p:
        if "IP" in p:
            if "TCP" in p:
                sess = str(
                    sorted(
                        [
                            "TCP",
                            p[scapy.IP].src,
                            p[scapy.TCP].sport,
                            p[scapy.IP].dst,
                            p[scapy.TCP].dport,
                        ],
                        key=str,
                    )
                )
            elif "UDP" in p:
                sess = str(
                    sorted(
                        [
                            "UDP",
                            p[scapy.IP].src,
                            p[scapy.UDP].sport,
                            p[scapy.IP].dst,
                            p[scapy.UDP].dport,
                        ],
                        key=str,
                    )
                )
            elif "ICMP" in p:
                sess = str(
                    sorted(
                        [
                            "ICMP",
                            p[scapy.IP].src,
                            p[scapy.IP].dst,
                            p[scapy.ICMP].code,
                            p[scapy.ICMP].type,
                            p[scapy.ICMP].id,
                        ],
                        key=str,
                    )
                )
            else:
                sess = str(
                    sorted(
                        ["IP", p[scapy.IP].src, p[scapy.IP].dst, p[scapy.IP].proto],
                        key=str,
                    )
                )
        elif "ARP" in p:
            sess = str(sorted(["ARP", p[scapy.ARP].psrc, p[scapy.ARP].pdst], key=str))
        # else:
        #     sess = p.sprintf("Ethernet type=%04xr,Ether.type%")
    return sess


def _layer2dict(obj):
    d = {}

    if not getattr(obj, "fields_desc", None):
        return
    for f in obj.fields_desc:
        value = getattr(obj, f.name)
        if value is type(None):  # pragma: no cover
            value = None

        if not isinstance(
            value, (int, float, str, bytes, bool, list, tuple, set, dict, type(None))
        ):
            value = _layer2dict(value)
        d[f.name] = value
    return {obj.name: d}


class _Pkt2Dict:
    def __init__(self, pkt):
        self.pkt = pkt

    def to_dict(self):
        """
        Turn every layer to dict, store in ChainMap type.
        `Reference <https://github.com/littlezz/scapy2dict>`__
        """
        d = list()
        count = 0

        while True:
            layer = self.pkt.getlayer(count)
            if not layer:
                break
            d.append(_layer2dict(layer))

            count += 1
        return dict(**collections.ChainMap(*list(filter(lambda x: x is not None, d))))


class PcapUSB:
    qwerty_map = {
        "04": "a",
        "05": "b",
        "06": "c",
        "07": "d",
        "08": "e",
        "09": "f",
        "0a": "g",
        "0b": "h",
        "0c": "i",
        "0d": "j",
        "0e": "k",
        "0f": "l",
        "10": "m",
        "11": "n",
        "12": "o",
        "13": "p",
        "14": "q",
        "15": "r",
        "16": "s",
        "17": "t",
        "18": "u",
        "19": "v",
        "1a": "w",
        "1b": "x",
        "1c": "y",
        "1d": "z",
        "1e": "1",
        "1f": "2",
        "20": "3",
        "21": "4",
        "22": "5",
        "23": "6",
        "24": "7",
        "25": "8",
        "26": "9",
        "27": "0",
        "2d": "-",
        "2e": "=",
        "2f": "[",
        "30": "]",
        "31": "\\",
        "32": "#",
        "33": ";",
        "34": "'",
        "35": "`",
        "36": ",",
        "37": ".",
        "38": "/",
        "28": "ENTER\n",
        "2c": " ",
        "4f": "RIGHTARROW",
        "50": "LEFTARROW",
        "51": "DOWNARROW",
        "52": "UPARROW",
        "4c": "DEL",
        "2a": "BACKSPACE",
        "3a": "F1",
        "3b": "F2",
        "3c": "F3",
        "3d": "F4",
        "3e": "F5",
        "3f": "F6",
        "40": "F7",
        "41": "F8",
        "42": "F9",
        "43": "F10",
        "44": "F11",
        "45": "F12",
    }
    qwerty_modifier = {
        "1e": "!",
        "1f": "@",
        "20": "#",
        "21": "$",
        "22": "%",
        "23": "^",
        "24": "&",
        "25": "*",
        "26": "(",
        "27": ")",
        "2b": "\t",
        "2c": " ",
        "2d": "_",
        "2e": "+",
        "2f": "{",
        "30": "}",
        "31": "|",
        "32": "~",
        "33": ":",
        "34": '"',
        "35": "~",
        "36": "<",
        "37": ">",
        "38": "?",
    }

    dvorak = {
        "04": "a",
        "05": "x",
        "06": "j",
        "07": "e",
        "08": ".",
        "09": "u",
        "0a": "i",
        "0b": "d",
        "0c": "c",
        "0d": "h",
        "0e": "t",
        "0f": "n",
        "10": "m",
        "11": "b",
        "12": "r",
        "13": "l",
        "14": "'",
        "15": "p",
        "16": "o",
        "17": "y",
        "18": "g",
        "19": "k",
        "1a": ",",
        "1b": "q",
        "1c": "f",
        "1d": ";",
        "1e": "1",
        "1f": "2",
        "20": "3",
        "21": "4",
        "22": "5",
        "23": "6",
        "24": "7",
        "25": "8",
        "26": "9",
        "27": "0",
        "2d": "[",
        "2e": "]",
        "2f": "/",
        "30": "=",
        "31": "\\",
        "33": "s",
        "34": "-",
        "35": "`",
        "36": "w",
        "37": "v",
        "38": "z",
    }

    dvorak_modifier = {
        "1e": "!",
        "1f": "@",
        "20": "#",
        "21": "$",
        "22": "%",
        "23": "^",
        "24": "&",
        "25": "*",
        "26": "(",
        "27": ")",
        "2b": "\t",
        "2c": " ",
        "2d": "{",
        "2e": "}",
        "2f": "?",
        "30": "+",
        "31": "|",
        "32": "~",
        "33": "S",
        "34": "_",
        "35": "~",
        "36": "<",
        "37": ">",
        "38": "?",
    }


class Pcap(chepy.core.ChepyCore):
    """This plugin allows handling of various pcap 
    related operations. 

    scapy is a requirement for this plugin.
    """

    def _pcap_reader_instance(self, bpf_filter):
        if sys.platform == "darwin":
            self._warning_logger("Need tcpdump from Brew for filter to work")
        if bpf_filter:
            return scapy.PcapReader(
                scapy.tcpdump(
                    self._pcap_filepath, args=["-w", "-", bpf_filter], getfd=True
                )
            )
        else:
            return scapy.PcapReader(self._pcap_filepath)

    @chepy.core.ChepyDecorators.call_stack
    def read_pcap(self):
        """Load a pcap. The state is set to scapy
        
        Returns:
            Chepy: The Chepy object. 
        """
        self._pcap_filepath = str(self._abs_path(self.state))
        self.state = "Pcap loaded"
        return self

    @chepy.core.ChepyDecorators.call_stack
    def pcap_dns_queries(self):
        """Get DNS queries and their frame numbers
        
        Returns:
            Chepy: The Chepy object. 

        Examples:
            >>> Chepy("tests/files/test.pcapng").read_pcap().pcap_dns_queries().o
            [
                b'fcmconnection.googleapis.com.',
                ...
                b'google.com.'
            ]
        """
        hold = []
        pcap = scapy.rdpcap(self._pcap_filepath)
        sessions = pcap.sessions(_full_duplex)
        for session in sessions:
            packets = sessions.get(session)
            for packet in packets:
                if not scapy.DNSQR in packet:
                    continue
                query = packet.getlayer("DNS").qd.qname
                hold.append(query)
        self.state = hold
        return self

    @chepy.core.ChepyDecorators.call_stack
    def pcap_http_streams(self):
        """Get a dict of HTTP req/res 

        This method does full fully assemble when data exceeds a 
        certain threshold. 
        
        Returns:
            Chepy: The Chepy object. 
        """
        hold = []
        pcap = scapy.rdpcap(self._pcap_filepath)
        sessions = pcap.sessions(_full_duplex)
        for session in sessions:
            packets = sessions.get(session)
            req_res = {"request": {}, "response": {}}
            for packet in packets:
                if not scapy_http.HTTP in packet:
                    continue
                if scapy_http.HTTPRequest in packet:
                    req_res["request"]["headers"] = packet.getlayer(
                        scapy_http.HTTPRequest
                    ).fields
                    if scapy.Raw in packet:
                        req_res["request"]["payload"] = packet.getlayer(scapy.Raw).load
                    else:
                        req_res["request"]["payload"] = {}
                if scapy_http.HTTPResponse in packet:
                    req_res["response"]["headers"] = packet.getlayer(
                        scapy_http.HTTPResponse
                    ).fields
                    if scapy.Raw in packet:
                        req_res["response"]["payload"] = packet.getlayer(scapy.Raw).load
                    else:  # pragma: no cover
                        req_res["response"]["payload"] = {}
            if len(req_res.get("request")):
                hold.append(req_res)

        self.state = hold
        return self

    @chepy.core.ChepyDecorators.call_stack
    def pcap_payload(self, layer: str, bpf_filter: str = ""):
        """Get an array of payloads based on provided layer
        
        Args:
            layer (str): Required. A valid Scapy layer.
            bpf_filter (str, optional): Apply a BPF filter to the packets 
        
        Returns:
            Chepy: The Chepy object. 
        """
        hold = []
        for packet in self._pcap_reader_instance(bpf_filter):
            if not layer in packet:
                continue
            check_raw = scapy.Raw in packet
            if check_raw:
                hold.append(packet.getlayer(scapy.Raw).load)
        self.state = hold
        return self

    @chepy.core.ChepyDecorators.call_stack
    def pcap_payload_offset(
        self, layer: str, start: int, end: int = None, bpf_filter: str = ""
    ):
        """Dump the raw payload by offset. 
        
        Args:
            layer (str): The layer to get the data from. 
            start (int): The starting offset of the data to be extracted. 
                This could be a negative index number.
            end (int, optional): The end index of the offset.
            bpf_filter (str, optional): Apply a BPF filter to the packets
        
        Returns:
            Chepy: The Chepy object. 

        Examples:
            In this example, we are extracting all the payloads from the last 20 bytes on 
            on the ICMP layer. 
            
            >>> Chepy('tests/files/test.pcapng').read_pcap().pcap_payload_offset('ICMP', -20)
            [b'secret', b'message']
        """
        hold = []

        for packet in self._pcap_reader_instance(bpf_filter):
            if not layer in packet:
                continue
            if not scapy.Raw in packet:  # pragma: no cover
                continue
            load = packet.getlayer("Raw").load
            hold.append(load[start:end])
        self.state = hold
        return self

    @chepy.core.ChepyDecorators.call_stack
    def pcap_to_dict(self, bpf_filter: str = ""):
        """Convert a pcap to a dict

        Args:
            bpf_filter (str, optional): Apply a BPF filter to the packets
        
        Returns:
            Chepy: The Chepy object. 
        """
        hold = []
        for packet in self._pcap_reader_instance(bpf_filter):
            hold.append(_Pkt2Dict(packet).to_dict())
        self.state = hold
        return self

    @chepy.core.ChepyDecorators.call_stack
    def pcap_layer_stats(self, bpf_filter: str = ""):
        """Get a count of all layers in the pcap

        Args:
            bpf_filter (str, optional): Apply a BPF filter to the packets
        
        Returns:
            Chepy: The Chepy object. 
        """

        def get_layers(pkt):
            yield pkt.name
            while pkt.payload:
                pkt = pkt.payload
                yield pkt.name

        layer_dict = collections.OrderedDict()
        for packet in self._pcap_reader_instance(bpf_filter):
            for key in list(get_layers(packet)):
                if layer_dict.get(key):
                    layer_dict[key] += 1
                else:
                    layer_dict[key] = 1

        self.state = dict(layer_dict)
        return self

    def pcap_convos(self, bpf_filter: str = ""):
        """Get layer 3 conversation states

        Args:
            bpf_filter (str, optional): Apply a BPF filter to the packets
        
        Returns:
            Chepy: The Chepy object. 
        """
        convo = collections.OrderedDict()

        for packet in self._pcap_reader_instance(bpf_filter):
            if not scapy.IP in packet:  # pragma: no cover
                continue
            ip_layer = packet.getlayer(scapy.IP)
            src = ip_layer.src
            dst = ip_layer.dst
            layer_3 = packet.getlayer(2).name
            if not convo.get(src):
                convo[src] = {}
            if convo[src].get(layer_3):
                if dst not in convo[src][layer_3]:
                    convo[src][layer_3].append(dst)
            else:
                convo[src][layer_3] = [dst]
        self.state = dict(convo)
        return self

    @chepy.core.ChepyDecorators.call_stack
    def pcap_usb_keyboard(self, layout: str = "qwerty"):
        """Decode usb keyboard pcap
        
        Args:
            layout (str, optional): Layout of the keyboard. Defaults to "qwerty".
        
        Raises:
            TypeError: If layout is not qwerty or dvorak
        
        Returns:
            Chepy: The Chepy object. 
        """
        if layout == "qwerty":
            key_map = PcapUSB.qwerty_map
            shift_modifier = PcapUSB.qwerty_modifier
        elif layout == "dvorak":  # pragma: no cover
            key_map = PcapUSB.dvorak
            shift_modifier = PcapUSB.dvorak_modifier
        else:  # pragma: no cover
            raise TypeError("Valid layouts are qwerty and dvorak")

        packets = scapy.PcapReader(self._pcap_filepath)
        hold = []

        for packet in packets:
            if not scapy.Raw in packet:  # pragma: no cover
                continue
            load = packet.getlayer("Raw").load
            key_press = binascii.hexlify(load)[-16:]
            if key_press == "0000000000000000":  # pragma: no cover
                continue
            shift, _, key = re.findall(b".{2}", key_press)[0:3]
            shift_pressed = bool(shift == b"02")
            pressed = key_map.get(key.decode())
            if shift_pressed:
                special = shift_modifier.get(key.decode())
                if special:
                    hold.append(special)
                elif pressed:
                    hold.append(pressed.upper())
            elif pressed:
                hold.append(pressed)
        self.state = "".join(hold)
        return self
