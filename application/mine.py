from .block import Block
from .models import Pendings, Blocks, Utxo
from .serializer import Deserializer, CoinbaseDeserializer
from .original_coinbase import OriginalCoinbase
import os
import time
import json
import hashlib


class Mine:

    def __init__(self):
        self.fee = 0

    def mine(self):
        pending_pool_arr = Pendings.objects.all()
        if len(pending_pool_arr) < 1:
            return 'Need more transactions!'
        else:
            list = []
            index = 0
            while index < 3:
                if index < len(pending_pool_arr):
                    list.append(pending_pool_arr[index].raw_tx)
                index += 1

            timestamp = int(time.time())
            prev_block_height, prev_block_hash = self.prev_block_hash_height()
            transaction = list
            for tx in transaction:
                Pendings.objects.filter(raw_tx=tx).delete()
                deserialized = Deserializer(tx)
                found_tx = self.search_for_tx_hash_utxo(deserialized.tx_out_hash_1)
                if len(found_tx):
                    amount = int(found_tx[0].amount)

                    self.utxo_delete(deserialized.tx_out_hash_1)
                    if deserialized.tx_out_count_1 == 1:
                        self.utxo_insert_regular(tx)
                    else:
                        self.utxo_insert_regular(tx)
                        self.utxo_insert_regular(tx, True)

                    if deserialized.tx_out_count_1 == 1:
                        self.fee = int(amount) - int(deserialized.tx_out_value_1)
                    else:
                        self.fee = int(amount) - (int(deserialized.tx_out_value_1) + int(deserialized.tx_out_value_2))
                else:
                    del tx
            coinbase = OriginalCoinbase(self.fee)
            c_tx = coinbase.raw_coinbase()
            deserialized = CoinbaseDeserializer(c_tx.hex())
            self.utxo_delete(deserialized.tx_out_hash_1)
            self.coinbase_to_utxo(c_tx.hex(), int(self.fee) + 5000000000)

            list = [c_tx.hex()]
            for tx in transaction:
                list.append(tx)

            new_block = Block(timestamp, prev_block_hash, list, int(prev_block_height) + 1)
            new_block.blockhash = new_block.hash(0)
            new_block.saveBlockToDb()
            return True

    def prev_block_hash_height(self):
        last_block_info = Blocks.objects.latest('id')
        return last_block_info.height, last_block_info.block_hash

    def search_for_tx_hash_utxo(self, current_tx_hash):
        utxo = Utxo.objects.filter(tx_hash=current_tx_hash)
        return utxo

    def utxo_delete(self, current_tx_hash):
        Utxo.objects.filter(tx_hash=current_tx_hash).delete()

    def utxo_insert_regular(self, tx, change=False):
        recipient_address = Deserializer(tx)
        tx_hash = hashlib.sha256(bytes.fromhex(tx)).digest()
        tx_hash = hashlib.sha256(tx_hash).digest()
        if not change:
            utxo = Utxo(tx_hash=str(tx_hash.hex()), tx_raw=str(recipient_address.raw_tx), output_number='0',
                        amount=str(recipient_address.tx_out_value_1), address=recipient_address.recipient_1)
            utxo.save()
            return True
        else:
            utxo = Utxo(tx_hash=str(tx_hash.hex()), tx_raw=str(recipient_address.raw_tx), output_number='0',
                        amount=str(recipient_address.tx_out_value_2), address=str(recipient_address.recipient_2))
            utxo.save()
        return True

    def coinbase_to_utxo(self, tx, fee):
        recipient_address = CoinbaseDeserializer(tx)
        tx_hash = hashlib.sha256(bytes.fromhex(tx)).digest()
        tx_hash = hashlib.sha256(tx_hash).digest()
        utxo = Utxo(tx_hash=str(tx_hash.hex()), tx_raw=str(recipient_address.raw_tx), output_number='0', amount=fee,
                    address=recipient_address.sender_1)
        utxo.save()
        return True
