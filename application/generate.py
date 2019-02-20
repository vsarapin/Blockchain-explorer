from binascii import hexlify, unhexlify
from ecdsa import SigningKey, VerifyingKey, SECP256k1, util
from base58 import b58encode, b58decode, b58decode_check
import hashlib
import codecs

def ripemd160(x):
    d = hashlib.new('ripemd160')
    d.update(x)
    return d


class Generate:
    def __init__(self, ):
        pass

    def generate_keys(self):
        private_key = SigningKey.generate(curve=SECP256k1, hashfunc=hashlib.sha256)
        private_key = hexlify(private_key.to_string()).decode('ascii').upper()

        extended_key = '80' + private_key
        first_sha256 = hashlib.sha256(unhexlify(extended_key)).hexdigest()
        second_sha256 = hashlib.sha256(unhexlify(first_sha256)).hexdigest()
        final_key = extended_key + second_sha256[:8]
        WIF = b58encode(unhexlify(final_key)).decode('utf-8')
        private_key_bytes = unhexlify(private_key)
        key = SigningKey.from_string(private_key_bytes, curve=SECP256k1, hashfunc=hashlib.sha256).verifying_key
        key_bytes = key.to_string()
        key_hex = codecs.encode(key_bytes, 'hex')
        public_key = '04' + key_hex.decode('utf-8').upper()

        hash160 = ripemd160(hashlib.sha256(unhexlify(public_key)).digest()).digest()
        publ_addr_a = b"\x00" + hash160
        checksum = hashlib.sha256(hashlib.sha256(publ_addr_a).digest()).digest()[:4]
        publ_addr_b = b58encode(publ_addr_a + checksum)
        address = publ_addr_b.decode()
        content = private_key + ',' + WIF + ',' + public_key + ',' + address
        return content
