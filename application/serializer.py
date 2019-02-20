from base58 import b58encode, b58decode, b58decode_check, b58encode_check
import binascii
import codecs
import struct
import hashlib


class Serializer:
    def __init__(
            self,
            satoshis,
            previous_output,
            sender,
            recipient,
            coinbase,
            sigscript=False,
            signature=False):

        self.satoshis = satoshis
        self.sender = sender
        self.recipient = recipient
        self.signature = signature
        self.sigscript = sigscript
        self.previous_output = previous_output
        self.coinbase = coinbase

    def return_raw_transaction(self):
        recipient_hashed_pubkey = b58decode_check(self.recipient)[1:].hex()
        if not self.coinbase:
            my_hashed_pubkey = b58decode_check(self.sender)[1:].hex()
        else:
            my_hashed_pubkey = self.coinbase
        version = struct.pack("<L", 1)
        tx_in_count = struct.pack("<B", 1)
        tx_in = {}
        tx_out_count = struct.pack("<B", 1)
        tx_out = {}
        lock_time = struct.pack("<L", 0)

        # form tx_in
        if self.coinbase:
            tx_in_count = struct.pack("<B", 1)
            tx_out_count = struct.pack("<B", 1)
            tx_in['tx_out_hash'] = bytes.fromhex(self.flip_byte_order(self.previous_output))
            tx_in['tx_out_index'] = bytes.fromhex("ffffffff")
            height_of_block = (1).to_bytes(3, byteorder="little", signed=False)
            tx_in['script'] = b"\03" + height_of_block + self.coinbase
            tx_in['script_bytes'] = struct.pack("<B", len(tx_in["script"]))
        else:
            tx_in['tx_out_hash'] = bytes.fromhex(self.flip_byte_order(self.previous_output))
            tx_in['tx_out_index'] = struct.pack("<L", 1)
            tx_in['script'] = bytes.fromhex("76a914%s88ac" % my_hashed_pubkey)
            tx_in['script_bytes'] = struct.pack("<B", len(tx_in["script"]))
        tx_in['sequence'] = bytes.fromhex("ffffffff")

        # form tx_out
        tx_out['value'] = struct.pack("<Q", self.satoshis)
        tx_out['pk_script'] = bytes.fromhex("76a914%s88ac" % recipient_hashed_pubkey)
        tx_out['script_bytes'] = struct.pack("<B", len(tx_out["pk_script"]))
        # =========================================
        # form raw_tx
        if not self.sigscript:
            raw_tx_string = (
                    version
                    + tx_in_count
                    + tx_in['tx_out_hash']
                    + tx_in['tx_out_index']
                    + tx_in['script_bytes']
                    + tx_in['script']
                    + tx_in['sequence']
                    + tx_out_count
                    + tx_out['value']
                    + tx_out['script_bytes']
                    + tx_out['pk_script']
                    + lock_time
                    + struct.pack("<L", 1)
            )
            hashed_tx_to_sign = hashlib.sha256(hashlib.sha256(raw_tx_string).digest()).digest()
            return hashed_tx_to_sign
        else:
            real_tx = (
                    version
                    + tx_in_count
                    + tx_in['tx_out_hash']
                    + tx_in['tx_out_index']
                    + struct.pack("<B", len(self.sigscript) + 1)
                    + struct.pack("<B", len(self.signature) + 1)
                    + self.sigscript
                    + tx_in['sequence']
                    + tx_out_count
                    + tx_out['value']
                    + tx_out['script_bytes']
                    + tx_out['pk_script']
                    + lock_time
            )
            return real_tx

    def flip_byte_order(self, string):
        x = range(0, len(string), 2)
        flipped = "".join(reversed([string[i:i + 2] for i in x]))
        return flipped


class Deserializer:

    def __init__(self, serializedString):
        self.tmp_value = 0
        self.raw_tx = serializedString
        self.version_1 = self.version()
        self.tx_in_count_1 = self.tx_in_count()
        self.tx_out_hash_1 = self.tx_out_hash()
        self.tx_out_index_1 = self.tx_out_index()
        self.tx_in_bytes_1 = self.tx_in_bytes()
        self.sigscript_1 = self.sigscript()
        self.sequence_1 = self.sequence()
        self.tx_out_count_1 = self.tx_out_count()
        self.tx_out_value_1 = self.tx_out_value(False)
        self.tx_out_bytes_1 = self.tx_out_bytes(False)
        self.tx_out_script_1 = self.tx_out_script(False)
        self.sender_1 = self.sender(False)
        self.recipient_1 = self.recipient(False)
        self.sender_public_key_1 = self.sender_public_key(False)
        self.public_key_1 = self.hex_public_key(False)
        if self.tx_out_count_1 == 2:
            self.tx_out_value_2 = self.tx_out_value(True, self.tmp_value)
            self.tx_out_bytes_2 = self.tx_out_bytes(True)
            self.tx_out_script_2 = self.tx_out_script(True)
            self.sender_2 = self.sender(True)
            self.recipient_2 = self.recipient(True)
            self.sender_public_key_2 = self.sender_public_key(True)
            self.public_key_2 = self.hex_public_key(True)

    def version(self):
        return int(self.flip_byte_order(self.raw_tx[:8]), 16)

    def tx_in_count(self):
        return int(self.flip_byte_order(self.raw_tx[8:10]), 16)

    def tx_out_hash(self):
        # print(self.flip_byte_order(self.raw_tx[10:74]))
        return self.flip_byte_order(self.raw_tx[10:74])

    def tx_out_index(self):
        return int(self.flip_byte_order(self.raw_tx[74:82]), 16)

    def tx_in_bytes(self):
        return int(self.flip_byte_order(self.raw_tx[82:84]), 16)

    def sigscript(self):
        return self.raw_tx[84:84 + self.tx_in_bytes_1 * 2]

    def sequence(self):
        self.tmp_value = 84 + self.tx_in_bytes_1 * 2
        return int(self.raw_tx[self.tmp_value : self.tmp_value + 8], 16)

    def tx_out_count(self):
        self.tmp_value = self.tmp_value + 8
        return int(self.raw_tx[self.tmp_value : self.tmp_value + 2], 16)

    def tx_out_value(self, repeat, value_from=0):
        if not repeat:
            self.tmp_value = self.tmp_value + 2
            # print (int(self.flip_byte_order(self.raw_tx[self.tmp_value: self.tmp_value + 16]), 16))
            return int(self.flip_byte_order(self.raw_tx[self.tmp_value : self.tmp_value + 16]), 16)
        else:
            self.tmp_value = value_from
            # print (int(self.flip_byte_order(self.raw_tx[self.tmp_value : self.tmp_value + 16]), 16))
            return int(self.flip_byte_order(self.raw_tx[self.tmp_value : self.tmp_value + 16]), 16)


    def tx_out_bytes(self, repeat):
        if not repeat:
            self.tmp_value = self.tmp_value + 16
            return int(self.flip_byte_order(self.raw_tx[self.tmp_value : self.tmp_value + 2]), 16)
        else:
            self.tmp_value = self.tmp_value + 16
            return int(self.flip_byte_order(self.raw_tx[self.tmp_value : self.tmp_value + 2]), 16)

    def tx_out_script(self, repeat):
        if not repeat:
            self.tmp_value = self.tmp_value + 2
            tx_out_script = self.raw_tx[self.tmp_value: self.tmp_value + self.tx_out_bytes_1 * 2]
            self.tmp_value += self.tx_out_bytes_1 * 2
            return tx_out_script
        else:
            self.tmp_value = self.tmp_value + 2
            tx_out_script = self.raw_tx[self.tmp_value: self.tmp_value + self.tx_out_bytes_2 * 2]
            self.tmp_value += self.tx_out_bytes_2 * 2
            return tx_out_script

    def sender(self, repeat):
        if not repeat:
            hash160 = self.ripemd160(hashlib.sha256(binascii.unhexlify(self.sigscript_1[-130:])).digest()).digest()
            publ_addr_a = b"\x00" + hash160
            checksum = hashlib.sha256(hashlib.sha256(publ_addr_a).digest()).digest()[:4]
            publ_addr_b = b58encode(publ_addr_a + checksum)
            return publ_addr_b.decode()
        else:
            hash160 = self.ripemd160(hashlib.sha256(binascii.unhexlify(self.sigscript_1[-130:])).digest()).digest()
            publ_addr_a = b"\x00" + hash160
            checksum = hashlib.sha256(hashlib.sha256(publ_addr_a).digest()).digest()[:4]
            publ_addr_b = b58encode(publ_addr_a + checksum)
            return publ_addr_b.decode()

    def recipient(self, repeat):
        if not repeat:
            return b58encode_check(b'\x00' +  codecs.decode(self.tx_out_script_1[6:len(self.tx_out_script_1) - 4], 'hex')).decode()
        else:
            return b58encode_check(b'\x00' +  codecs.decode(self.tx_out_script_2[6:len(self.tx_out_script_2) - 4], 'hex')).decode()

    def sender_public_key(self, repeat):
        if not repeat:
            return self.sigscript_1[-130:]
        else:
            return self.sigscript_1[-130:]

    def hex_public_key(self, repeat):
        if not repeat:
            return bytes.fromhex(self.sender_public_key_1)
        else:
            return bytes.fromhex(self.sender_public_key_2)

    def ripemd160(self, x):
        d = hashlib.new('ripemd160')
        d.update(x)
        return d

    def flip_byte_order(self, string):
        x = range(0, len(string), 2)
        flipped = "".join(reversed([string[i:i + 2] for i in x]))
        return flipped


class CoinbaseDeserializer:

    def __init__(self, serializedString):
        self.tmp_value = 0
        self.raw_tx = serializedString
        self.version_1 = self.version()
        self.tx_in_count_1 = self.tx_in_count()
        self.tx_out_hash_1 = self.tx_out_hash()
        self.tx_out_index_1 = self.tx_out_index()
        self.tx_in_bytes_1 = self.tx_in_bytes()
        self.sigscript_1 = self.sigscript()
        self.sequence_1 = self.sequence()
        self.tx_out_count_1 = self.tx_out_count()
        self.tx_out_value_1 = self.tx_out_value()
        self.tx_out_bytes_1 = self.tx_out_bytes()
        self.tx_out_script_1 = self.tx_out_script()
        self.sender_1 = self.sender()
        self.recipient_1 = self.recipient()
        self.sender_public_key_1 = self.sender_public_key()
        self.public_key_1 = self.hex_public_key()

    def version(self):
        return int(self.flip_byte_order(self.raw_tx[:8]), 16)

    def tx_in_count(self):
        return int(self.flip_byte_order(self.raw_tx[8:10]), 16)

    def tx_out_hash(self):
        return self.raw_tx[10:42]

    def tx_out_index(self):
        return self.raw_tx[42:50]

    def tx_in_bytes(self):
        return int(self.flip_byte_order(self.raw_tx[50:52]), 16)

    def sigscript(self):
        return self.raw_tx[52:52 + self.tx_in_bytes_1 * 2]

    def sequence(self):
        self.tmp_value = 52 + self.tx_in_bytes_1 * 2
        return int(self.raw_tx[self.tmp_value: self.tmp_value + 8], 16)

    def tx_out_count(self):
        self.tmp_value = self.tmp_value + 8
        return int(self.raw_tx[self.tmp_value: self.tmp_value + 2], 16)

    def tx_out_value(self):
        self.tmp_value = self.tmp_value + 2
        return int(self.flip_byte_order(self.raw_tx[self.tmp_value: self.tmp_value + 16]), 16)

    def tx_out_bytes(self):
        self.tmp_value = self.tmp_value + 16
        return int(self.flip_byte_order(self.raw_tx[self.tmp_value: self.tmp_value + 2]), 16)

    def tx_out_script(self):
        self.tmp_value = self.tmp_value + 2
        return self.raw_tx[self.tmp_value: self.tmp_value + self.tx_out_bytes_1 * 2]

    def sender(self):
        hash160 = self.ripemd160(hashlib.sha256(binascii.unhexlify(self.sigscript_1[-130:])).digest()).digest()
        publ_addr_a = b"\x00" + hash160
        checksum = hashlib.sha256(hashlib.sha256(publ_addr_a).digest()).digest()[:4]
        publ_addr_b = b58encode(publ_addr_a + checksum)
        return publ_addr_b.decode()

    def recipient(self):
        return b58encode_check(
            b'\x00' + codecs.decode(self.tx_out_script_1[6:len(self.tx_out_script_1) - 4], 'hex')).decode()

    def sender_public_key(self):
        return self.sigscript_1[-130:]

    def hex_public_key(self):
        return bytes.fromhex(self.sender_public_key_1)

    def ripemd160(self, x):
        d = hashlib.new('ripemd160')
        d.update(x)
        return d

    def flip_byte_order(self, string):
        x = range(0, len(string), 2)
        flipped = "".join(reversed([string[i:i + 2] for i in x]))
        return flipped


if __name__ == '__main__':
    Deserializer('01000000018160491a3bc27856a16868a82ba06460150167d9996dc7a1433460d556b686e3000000008b48304502210086890dae2311d4c9f8ab4de4836c96f877a51a19e5714d3a94aa60cfac57419402202ae32c4db2a7bf7cd8ec2924cf0577cec43dc4137134ea4fdc6c72d4d05b54e1014104e026954573a8cd624daf847baaae054e7bf1e2dbe9821f813f734e1e926cc918eeda2bb7464f1e465034881736841001ac1b139ee35a64c43c57293338d983d1ffffffff02000eaca9585bf0061976a914d2193c245e5d2d8d3993fd0b6579d03d3f65cd2188ac00c2eb0b000000001976a914d2193c245e5d2d8d3993fd0b6579d03d3f65cd2188ac00000000')