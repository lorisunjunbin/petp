import logging

from core.processor import Processor
from hashlib import (
    blake2b,
    blake2s,
    md5,
    sha1,
    sha3_224,
    sha3_256,
    sha3_384,
    sha3_512,
    sha224,
    sha256,
    sha384,
    sha512,
)


class HASH_STRProcessor(Processor):
    TPL: str = '{"inbound":"","outbound_key":"","algorithms":"blake2b | blake2s | md5 | sha1 | sha224 | sha256 | sha384 | sha3_224 | sha3_256 | sha3_384 | sha3_512 | sha512"}'

    DESC: str = f''' 
        Support hash string with algorithms: blake2b, blake2s, md5, sha1, sha224, sha256, sha384, sha3_224, sha3_256, sha3_384, sha3_512, sha512.
        {TPL}
    '''

    HASHING_ALGORITHMS = {
        "blake2b": blake2b,
        "blake2s": blake2s,
        "md5": md5,
        "sha1": sha1,
        "sha224": sha224,
        "sha256": sha256,
        "sha384": sha384,
        "sha3_224": sha3_224,
        "sha3_256": sha3_256,
        "sha3_384": sha3_384,
        "sha3_512": sha3_512,
        "sha512": sha512,
    }

    def process(self):
        inbound = self.expression2str(self.get_param('inbound'))
        algorithms = self.get_param("algorithms")
        outbound_key = self.get_param("outbound_key")
        outbound = None

        if self.has_hashing_algo(algorithms):
            outbound = self.hash_val(inbound, algorithms)
        else:
            logging.warning(f"Unknown algorithms: {algorithms}")

        logging.debug(f'{inbound} --[ hash via {algorithms}]--> {outbound}')

        self.populate_data(outbound_key, outbound)

    def has_hashing_algo(self, algorithms: str) -> bool:
        return algorithms.lower().strip() in self.HASHING_ALGORITHMS

    def hash_val(self, inbound: str | bytes, algorithms: str) -> str:
        if isinstance(inbound, str):
            inbound = inbound.encode()
        hashing_fn = self.HASHING_ALGORITHMS[algorithms.lower().strip()]
        return hashing_fn(inbound).hexdigest()
