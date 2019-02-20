from .validator import Validator
from .serializer import Serializer, Deserializer, CoinbaseDeserializer
from .models import Inputs, Outputs, Blocks
import hashlib
import codecs
import json
import sys

sys.setrecursionlimit(10000)


class Block:

    def __init__(self, timestamp, previous_hash, transactions, height):
        self.version = 1
        self.prev_hash = previous_hash
        self.timestamp = timestamp
        self.tx = transactions
        self.merkle_root = self.merkle_root(self.tx)
        self.height = height
        self.nonce = ''
        self.blockhash = ''

    def hash(self, nonce):
        version = self.version.to_bytes(4, byteorder="little", signed=False)
        previous_hash = codecs.decode(self.prev_hash, 'hex')
        timestamp = self.timestamp.to_bytes(4, byteorder="little", signed=False)
        merkle_root = codecs.decode(self.merkle_root, 'hex')

        new_nonce = (nonce).to_bytes(4, byteorder="little", signed=False)
        concat = version + new_nonce + previous_hash + merkle_root + timestamp
        concat = hashlib.sha256(concat)
        concat = concat.digest().hex()
        if concat[:2] != '00':
            return self.hash(nonce + 1)
        if concat[:2] == '00':
            self.nonce = nonce
            self.blockhash = concat
            index = 0
            for tx in self.tx:
                if index == 0:
                    tx_hash = hashlib.sha256(bytes.fromhex(tx)).digest()
                    tx_hash = hashlib.sha256(tx_hash).digest()
                    deserialized = CoinbaseDeserializer(tx)
                    inputs = Inputs(sigscript =  str(deserialized.sigscript_1), value = "5000000000", address_from = "0" * 32, block_hash=str(self.blockhash), prev_output=str(deserialized.tx_out_hash_1), outpoint=str(deserialized.tx_out_index_1), sequence=str(deserialized.sequence_1), tx_hash=str(tx_hash.hex()))
                    inputs.save()
                    outputs = Outputs(value = str(deserialized.tx_out_value_1), address_to = str(deserialized.sender_1), type="coinbase", scriptpubkey_hex=str(deserialized.tx_out_script_1), spending_tx="Unspent", tx_hash=str(tx_hash.hex()))
                    outputs.save()
                else:
                    deserialized = Deserializer(tx)
                    if deserialized.tx_out_count_1 == 1:
                        tx_hash = hashlib.sha256(bytes.fromhex(tx)).digest()
                        tx_hash = hashlib.sha256(tx_hash).digest()
                        deserialized = Deserializer(tx)
                        inputs = Inputs(sigscript =  str(deserialized.sigscript_1), address_from = str(deserialized.sender_1), block_hash=str(self.blockhash), prev_output=str(deserialized.tx_out_hash_1),
                                        outpoint=str(deserialized.tx_out_index_1),
                                        sequence=str(deserialized.sequence_1), tx_hash=str(tx_hash.hex()))
                        inputs.save()
                        outputs = Outputs(value = str(deserialized.tx_out_value_1), address_to = str(deserialized.recipient_1), type="regular", scriptpubkey_hex=str(deserialized.tx_out_script_1),
                                          spending_tx="Unspent", tx_hash=str(tx_hash.hex()))
                        outputs.save()
                    else:
                        tx_hash = hashlib.sha256(bytes.fromhex(tx)).digest()
                        tx_hash = hashlib.sha256(tx_hash).digest()
                        deserialized = Deserializer(tx)
                        inputs = Inputs(sigscript = str(deserialized.sigscript_1), address_from = str(deserialized.sender_1), block_hash=str(self.blockhash), prev_output=str(deserialized.tx_out_hash_1), outpoint=str(deserialized.tx_out_index_1), sequence=str(deserialized.sequence_1), tx_hash=str(tx_hash.hex()))
                        inputs.save()
                        outputs = Outputs(value = str(deserialized.tx_out_value_1), address_to = str(deserialized.recipient_1), type="regular", scriptpubkey_hex=str(deserialized.tx_out_script_1), spending_tx="Unspent", tx_hash=str(tx_hash.hex()))
                        outputs.save()
                        outputs_1 = Outputs(value = str(deserialized.tx_out_value_2), address_to = str(deserialized.recipient_2), type="regular", scriptpubkey_hex=str(deserialized.tx_out_script_2), spending_tx="Unspent", tx_hash=str(tx_hash.hex()))
                        outputs_1.save()
                index += 1
        return concat

    def saveBlockToDb(self):
        block = Blocks(version=str(self.version), height=str(self.height), nonce=str(self.nonce), block_hash=str(self.blockhash), previous_block_hash=str(self.prev_hash), merkle_root=str(self.merkle_root), timestamp=str(self.timestamp), number_of_transactions=str(len(self.tx)))
        block.save()
        return True

    def double_hash(self, a, b):
        # Reverse inputs before and after hashing
        # due to big-endian / little-endian nonsense
        a1 = codecs.decode(a, 'hex')[::-1]
        b1 = codecs.decode(b, 'hex')[::-1]
        h = hashlib.sha256(hashlib.sha256(a1 + b1).digest()).digest()
        return codecs.encode(h[::-1], 'hex')

    def merkle_root(self, hashList):
        if len(hashList) == 1:
            return hashList[0]
        newHashList = []
        # Process pairs. For odd length, the last is skipped
        for i in range(0, len(hashList) - 1, 2):
            newHashList.append(self.double_hash(hashList[i], hashList[i + 1]))
        if len(hashList) % 2 == 1:  # odd, hash last item twice
            newHashList.append(self.double_hash(hashList[-1], hashList[-1]))
        return self.merkle_root(newHashList)
