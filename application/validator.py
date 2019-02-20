from binascii import hexlify, unhexlify
from ecdsa import SigningKey, VerifyingKey, SECP256k1, util
from base58 import b58encode, b58decode, b58decode_check
import hashlib

def ripemd160(x):
    d = hashlib.new('ripemd160')
    d.update(x)
    return d

class Validator:
    def decode_base58(self, bc, length):
        # https://rosettacode.org/wiki/Bitcoin/address_validation
        digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        n = 0
        for char in bc:
            try:
                n = n * 58 + digits58.index(char)
            except ValueError:
                return False
        try:
            result = n.to_bytes(length, 'big')
            return result
        except OverflowError:
            return False

    def check_bc(self, bc):
        bcbytes = self.decode_base58(bc, 25)
        if not bcbytes:
            return False
        if bcbytes[-4:] == hashlib.sha256(hashlib.sha256(bcbytes[:-4]).digest()).digest()[:4]:
            return True
        else:
            return False

    def bcSenderAdress(self, path):
        if fileExists(path):
            file = open(path, 'r')
            address = file.read()
            file.close()
            return address
        else:
            print('Файл не существует. Нужно импортировать адрес из privkey')
            return False

    def compareAddresses(self, public_key, address_1):
        hash160 = ripemd160(hashlib.sha256(public_key).digest()).digest()
        publ_addr_a = b"\x00" + hash160
        checksum = hashlib.sha256(hashlib.sha256(publ_addr_a).digest()).digest()[:4]
        publ_addr_b = b58encode(publ_addr_a + checksum)
        address_2 = publ_addr_b.decode()
        if address_1 == address_2:
            return True
        else:
            return False

    def verifySignature(self, public_key, signature, hash):
        print(signature.hex())
        print(hash.hex())
        exit(1)
        public_key = bytes.fromhex(public_key[1:].hex())
        vk = VerifyingKey.from_string(public_key, curve=SECP256k1)
        return vk.verify(signature, hash)  # True/False
