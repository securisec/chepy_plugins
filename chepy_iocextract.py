import chepy.core
import logging

try:
    import iocextract as iocextract_lib
except ImportError:
    logging.warning("Could not import iocextract. Use pip install iocextract")

# # https://github.com/InQuest/python-iocextract
class iocextract(chepy.core.ChepyCore):
    """ Extracts URLs, IP addresses, MD5/SHA hashes, email addresses, and YARA rules from text corpora. It includes some encoded and "defanged" IOCs in the output, and optionally decodes/refangs them."""

    @chepy.core.ChepyDecorators.call_stack
    def iocextract(self, types: list = ['url', 'ip', 'email', 'hash', 'yara'], refang: bool = True, strip: bool = False):
        """ Method to extract IOCs from a text corpora
        Input:
            State: Text blob
            types: list, The types of IOC to extract, default is all (url, ip, email, hash + yara)
            refang: bool, Refang IOCs after extraction? Only applies to url, ip, email
            strip: bool, _Try_ and strip garbage data from urls. Only applies to url
        Returns:
            Chepy: The chepy object - A text list of found IOCs (joined by \\n)
        """
        text_blob = self.state

        extracted_iocs = []

        extracted_iocs += list(iocextract_lib.extract_urls(text_blob,  refang=refang, strip=strip) if 'url' in types else [])
        extracted_iocs += list(iocextract_lib.extract_ips(text_blob,  refang=refang) if 'ip' in types else [])
        extracted_iocs += list(iocextract_lib.extract_emails(text_blob,  refang=refang) if 'email' in types else [])
        extracted_iocs += list(iocextract_lib.extract_hashes(text_blob) if 'hash' in types else [])
        extracted_iocs += list(iocextract_lib.extract_yara_rules(text_blob) if 'yara' in types else [])

        self.state = '\n'.join(extracted_iocs)
        return self
