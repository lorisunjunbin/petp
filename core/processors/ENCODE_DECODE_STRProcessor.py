import logging

from core.processor import Processor
from base64 import (
    a85decode,
    a85encode,
    b16decode,
    b16encode,
    b32decode,
    b32encode,
    b32hexdecode,
    b32hexencode,
    b64decode,
    b64encode,
    b85decode,
    b85encode,
)
from binascii import hexlify, unhexlify


class ENCODE_DECODE_STRProcessor(Processor):
    TPL: str = '{"type":"ENCODE | DECODE", "inbound":"","outbound_key":"","algorithms":"base64 | base85 | hexlify | a85 | base16 | base32 | base32hex"}'

    DESC: str = f''' 
        Support encode/decode string with algorithms: base64, base85, hexlify, a85, base16, base32, base32hex.
        {TPL}
    '''

    ENCODING_ALGORITHMS: dict = {
        "a85": a85encode,
        "base16": b16encode,
        "base32": b32encode,
        "base32hex": b32hexencode,
        "base64": b64encode,
        "base85": b85encode,
        "hexlify": hexlify,
    }

    DECODING_ALGORITHMS: dict = {
        "a85": a85decode,
        "base16": b16decode,
        "base32": b32decode,
        "base32hex": b32hexdecode,
        "base64": b64decode,
        "base85": b85decode,
        "hexlify": unhexlify,
    }

    def get_category(self) -> str:
        return super().CATE_DATA_PROCESSING

    def process(self):
        inbound = self.expression2str(self.get_param('inbound'))
        type = self.get_param("type")
        algorithms = self.get_param("algorithms")
        outbound_key = self.get_param("outbound_key")
        outbound = None

        if type == "ENCODE" and self.has_encoding_algo(algorithms):
            outbound = self.encode(inbound, algorithms)
        elif type == "DECODE" and self.has_decoding_algo(algorithms):
            outbound = self.decode(inbound, algorithms)
        else:
            logging.warning(f"Unknown type: {type} or algorithms: {algorithms}")

        logging.debug(f'{inbound} --[{type} via {algorithms}]--> {outbound}')

        self.populate_data(outbound_key, outbound)

    def has_encoding_algo(self, algo: str) -> bool:
        return algo.lower().strip() in self.ENCODING_ALGORITHMS

    def has_decoding_algo(self, algo: str) -> bool:
        return algo.lower().strip() in self.DECODING_ALGORITHMS

    def encode(self, inbound: str | bytes, algorithms: str) -> str:
        if isinstance(inbound, str):
            inbound = inbound.encode()
        encoding_fn = self.ENCODING_ALGORITHMS[algorithms.lower().strip()]
        return encoding_fn(inbound).decode()

    def decode(self, inbound: str | bytes, algorithms: str) -> str:
        if isinstance(inbound, str):
            inbound = inbound.encode()
        decoding_fn = self.DECODING_ALGORITHMS[algorithms.lower().strip()]
        return decoding_fn(inbound).decode()
