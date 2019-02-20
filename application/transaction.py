from base58 import b58encode, b58decode, b58decode_check
from ecdsa import SigningKey, VerifyingKey, SECP256k1, util
from django.db import connection
import struct
import hashlib
import codecs
import json


class RawTx:
    version = struct.pack("<L", 1)
    tx_in_count = struct.pack("<B", 1)
    tx_out_count = struct.pack("<B", 1)
    lock_time = struct.pack("<L", 0)


class Transaction:

    def __init__(self, sender, recipient, amount, fee, previous_output):
        self.sigscript = ''
        self.sender = sender
        self.recipient = recipient
        self.previous_output = previous_output
        self.amount = amount
        self.fee = fee

    def calculate_change(self):
        full_ammount = 0
        for key in self.tx_amount:
            full_ammount += int(key)
        return full_ammount - (self.amount + self.fee)

    def create_transaction(self):
        raw_transaction, rtx = self.tx_raw_hash(False, False)
        signature, public_key = self.signTransaction(raw_transaction)
        sigscript = self.sigscript_calculate(signature, public_key)

        real_transaction = self.tx_raw_hash(signature, sigscript)
        return real_transaction.hex()

    def search_senders_privkey(self, sender_address):
        with connection.cursor() as cursor:
            cursor.execute("SELECT private_key FROM application_generated WHERE address = %s", [sender_address])
            row = cursor.fetchone()
        if row:
            return row[0]

        with connection.cursor() as cursor:
            cursor.execute("SELECT private_key FROM application_miner WHERE address = %s", [sender_address])
            row = cursor.fetchone()
        if row:
            return row[0]
        return False

    def signTransaction(self, raw_tx_hash):
        private_key = self.search_senders_privkey(self.sender)
        sk = SigningKey.from_string(codecs.decode(private_key, "hex"), curve=SECP256k1)
        public_key = sk.get_verifying_key()
        public_key = bytes.fromhex('04') + public_key.to_string()
        signature = sk.sign(raw_tx_hash, sigencode=util.sigencode_der_canonize)
        return signature, public_key

    def tx_raw_hash(self, signature, sigscript):
        rtx = RawTx()
        rtx.recipient_hashed_pubkey = b58decode_check(self.recipient)[1:].hex()
        rtx.my_hashed_pubkey = b58decode_check(self.sender)[1:].hex()
        rtx.tx_in_count = struct.pack("<B", self.input_counter)
        rtx.tx_out_count = struct.pack("<B", self.output_counter)

        # form tx_in
        index = 0
        input_result = ''

        while index < self.input_counter:
            input_result += self.form_inputs(self.input_prev_hashes[index], int(self.vout[index]), rtx.my_hashed_pubkey, signature, sigscript)
            index += 1

        # form tx_out
        output_result = ''
        if self.calculate_change() > 0:
            output_result += self.form_outputs(rtx.my_hashed_pubkey, self.calculate_change())
            output_result += self.form_outputs(rtx.recipient_hashed_pubkey, int(self.amount))

        else:
            output_result = self.form_outputs(rtx.recipient_hashed_pubkey, int(self.amount))

        # Form raw_tx or real_tx
        if not sigscript:
            raw_tx_string = self.form_raw_tx(input_result, output_result, rtx, sigscript)
            hashed_tx_to_sign = hashlib.sha256(hashlib.sha256(raw_tx_string).digest()).digest()
            return hashed_tx_to_sign, rtx
        else:
            real_tx = self.form_raw_tx(input_result, output_result, rtx, sigscript)
            return real_tx

    def form_raw_tx(self, inputs, outputs, rtx, sigscript):
        if not sigscript:
            return (
                    rtx.version
                    + rtx.tx_in_count
                    + bytes.fromhex(inputs)
                    + bytes.fromhex(outputs)
                    + rtx.tx_out_count
                    + rtx.lock_time
                    + struct.pack("<L", 1)
            )
        else:
            return (
                    rtx.version
                    + rtx.tx_in_count
                    + bytes.fromhex(inputs)
                    + rtx.tx_out_count
                    + bytes.fromhex(outputs)
                    + rtx.lock_time
            )

    def form_inputs(self, tx_out_hash, tx_out_index, my_hashed_pubkey, signature, sigscript):
        if not sigscript:
            sequence = bytes.fromhex("ffffffff")
            tx_out_hash = bytes.fromhex(self.flip_byte_order(tx_out_hash))
            tx_out_index = struct.pack("<L", tx_out_index)
            script = bytes.fromhex("76a914%s88ac" % my_hashed_pubkey)
            script_bytes = struct.pack("<B", len(bytes.fromhex("76a914%s88ac" % my_hashed_pubkey)))
            res = tx_out_hash + tx_out_index + script_bytes + script + sequence
            return res.hex()
        else:
            tx_out_hash = bytes.fromhex(self.flip_byte_order(tx_out_hash))
            tx_out_index = struct.pack("<L", tx_out_index)
            len_sigscript = struct.pack("<B", len(sigscript) + 1)
            len_signature = struct.pack("<B", len(signature) + 1)
            sequence = bytes.fromhex("ffffffff")
            res = tx_out_hash + tx_out_index + len_sigscript + len_signature + sigscript + sequence
            return res.hex()

    def form_outputs(self, recipient_hashed_pubkey, value):
        script = bytes.fromhex("76a914%s88ac" % recipient_hashed_pubkey)
        script_bytes = struct.pack("<B", len(bytes.fromhex("76a914%s88ac" % recipient_hashed_pubkey)))
        res = struct.pack("<Q", value) + script_bytes + script
        return res.hex()

    def sigscript_calculate(self, signature, public_key_bytes_hex):
        return (
                signature
                + b'\01'
                + struct.pack("<B", len(bytes.fromhex(public_key_bytes_hex.hex())))
                + bytes.fromhex(public_key_bytes_hex.hex())
        )

    def flip_byte_order(self, string):
        x = range(0, len(string), 2)
        flipped = "".join(reversed([string[i:i + 2] for i in x]))
        return flipped
