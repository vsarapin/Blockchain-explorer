from binascii import hexlify, unhexlify
from ecdsa import SigningKey, VerifyingKey, SECP256k1, util
from base58 import b58encode, b58decode, b58decode_check
import hashlib
import codecs


def ripemd160(x):
    d = hashlib.new('ripemd160')
    d.update(x)
    return d


class Import:
    def import_key(self, key):
        WIF = key
        try:
            first_encode = b58decode(WIF)
        except ValueError:
            return 'Wrong WIF!'
        private_key_full = hexlify(first_encode)
        private_key = private_key_full[2:-8]

        private_key_bytes = unhexlify(private_key)
        try:
            key = SigningKey.from_string(private_key_bytes, curve=SECP256k1, hashfunc=hashlib.sha256).verifying_key
        except AssertionError:
            return 'Wrong WIF!'
        key_bytes = key.to_string()
        key_hex = codecs.encode(key_bytes, 'hex')
        public_key = '04' + key_hex.decode('utf-8').upper()

        hash160 = ripemd160(hashlib.sha256(unhexlify(public_key)).digest()).digest()
        publ_addr_a = b"\x00" + hash160
        checksum = hashlib.sha256(hashlib.sha256(publ_addr_a).digest()).digest()[:4]
        publ_addr_b = b58encode(publ_addr_a + checksum)
        address = publ_addr_b.decode()
        content = private_key.decode('utf-8').upper() + ',' + WIF + ',' + public_key + ',' + address
        return content
