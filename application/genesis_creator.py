from ecdsa import SigningKey, VerifyingKey, SECP256k1, util
from binascii import hexlify, unhexlify
from base58 import b58encode, b58decode, b58decode_check
from .serializer import CoinbaseDeserializer
from .coinbase_block import CoinbaseBlock
from .models import Utxo, Miner
import hashlib
import codecs
import struct
import json


class RawTx:
    version = struct.pack("<L", 1)
    tx_in_count = struct.pack("<B", 1)
    tx_in = {}
    tx_out_count = struct.pack("<B", 1)
    tx_out = {}
    lock_time = struct.pack("<L", 0)


class GenesisCreator:
    def __init__(self):
        self.previous_output = "0" * 32
        self.satoshis = 50 * 100000000
        self.recipient = 0
        self.unlocking_script = bytes.fromhex('14071990')
        self.pubkey = self.get_miners_pubkey()

    def create_genesis(self):
        raw_tx_hash, rtx = self.genesis_tx_raw_hash()
        signature, public_key = self.createSignature(raw_tx_hash)
        sigscript = self.sigscript_calculate(signature, public_key)
        real_tx = self.genesis_tx_real_hash(rtx, sigscript, signature)

        timestamp = 1231006505
        prev_block_hash = "0000000000000000000000000000000000000000000000000000000000000000"
        transaction = [real_tx]
        genesis_block = CoinbaseBlock(timestamp, prev_block_hash, [transaction[0].hex()], 1)
        genesis_block.blockhash = genesis_block.hash(0)
        genesis_block.saveBlockToDb()

        hash, raw_tx, vout, amount, address = self.genesis_coinbase_to_utxo(real_tx)
        utxo = Utxo(tx_hash = hash, tx_raw = raw_tx, output_number = vout, amount = amount, address = address)
        utxo.save()
        return '1'

    def genesis_coinbase_to_utxo(self, tx):
        recipient_address = CoinbaseDeserializer(tx.hex())
        tx_hash = hashlib.sha256(bytes.fromhex(tx.hex())).digest()
        tx_hash = hashlib.sha256(tx_hash).digest()
        return str(tx_hash.hex()), str(recipient_address.raw_tx), '0', '5000000000', recipient_address.sender_1

    def get_miners_pubkey(self):
        pub_key = Miner.objects.latest('id')
        return pub_key.public_key

    def get_miners_privkey(self):
        priv_key = Miner.objects.latest('id')
        return priv_key.private_key

    def genesis_tx_raw_hash(self):
        rtx = RawTx()
        rtx.miners_pubkey = self.pubkey

        # form tx_in
        rtx.tx_in_count = struct.pack("<B", 1)
        rtx.tx_out_count = struct.pack("<B", 1)
        rtx.tx_in['tx_out_hash'] = bytes.fromhex(self.previous_output)
        rtx.tx_in['tx_out_index'] = bytes.fromhex("ffffffff")
        rtx.height_of_block = (1).to_bytes(3, byteorder="little", signed=False)
        rtx.tx_in['script'] = b"\03" + rtx.height_of_block + self.unlocking_script
        rtx.tx_in['script_bytes'] = struct.pack("<B", len(rtx.tx_in["script"]))
        rtx.tx_in['sequence'] = bytes.fromhex("ffffffff")

        # form tx_out
        rtx.tx_out['value'] = struct.pack("<Q", self.satoshis)
        # https://bitcoin.stackexchange.com/questions/78866/variables-in-coinbase-transaction-decoding-i-o-scripts
        rtx.tx_out['pk_script'] = bytes.fromhex("76a914%s88ac" % rtx.miners_pubkey)
        rtx.tx_out['script_bytes'] = struct.pack("<B", len(rtx.tx_out["pk_script"]))

        # =========================================
        # form raw_tx
        raw_tx_string = (
                rtx.version
                + rtx.tx_in_count
                + rtx.tx_in['tx_out_hash']
                + rtx.tx_in['tx_out_index']
                + rtx.tx_in['script_bytes']
                + rtx.tx_in['script']
                + rtx.tx_in['sequence']
                + rtx.tx_out_count
                + rtx.tx_out['value']
                + rtx.tx_out['script_bytes']
                + rtx.tx_out['pk_script']
                + rtx.lock_time
                + struct.pack("<L", 1)
        )
        hashed_tx_to_sign = hashlib.sha256(hashlib.sha256(raw_tx_string).digest()).digest()
        return hashed_tx_to_sign, rtx

    def genesis_tx_real_hash(self, rtx, sigscript, signature):
        # form real_tx
        real_tx = (
                rtx.version
                + rtx.tx_in_count
                + rtx.tx_in['tx_out_hash']
                + rtx.tx_in['tx_out_index']
                + struct.pack("<B", len(sigscript) + 1)
                + struct.pack("<B", len(signature) + 1)
                + sigscript
                + rtx.tx_in['sequence']
                + rtx.tx_out_count
                + rtx.tx_out['value']
                + rtx.tx_out['script_bytes']
                + rtx.tx_out['pk_script']
                + rtx.lock_time
        )
        return real_tx

    def createSignature(self, raw_tx_hash):
        private_key = self.get_miners_privkey()
        sk = SigningKey.from_string(codecs.decode(private_key, "hex"), curve=SECP256k1)
        public_key = sk.get_verifying_key()
        public_key = bytes.fromhex('04') + public_key.to_string()
        signature = sk.sign(raw_tx_hash, sigencode=util.sigencode_der_canonize)
        return signature, public_key

    def sigscript_calculate(self, signature, public_key_bytes_hex):
        return (
                signature
                + b'\01'
                + struct.pack("<B", len(bytes.fromhex(public_key_bytes_hex.hex())))
                + bytes.fromhex(public_key_bytes_hex.hex())
        )
