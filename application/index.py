from .models import Blocks, Inputs, Outputs, Utxo
import codecs

import json
import datetime
from django.http import Http404


# timpestamp to readable format <datetime.datetime.fromtimestamp(ts_epoch).strftime('%Y/%m/%d, %H:%M:%S')>
class IndexBlocks:

    def __init__(self):
        pass

    def return_all_blocks(self):
        blocks = Blocks.objects.all()
        array = []
        if len(blocks):
            for block in blocks:
                array.append([
                    block.height,
                    datetime.datetime.fromtimestamp(int(block.timestamp)).strftime('%Y/%m/%d, %H:%M:%S'),
                    block.version,
                    block.number_of_transactions])
            return json.dumps(array)
        return 0

    def return_block_info(self, current_height):
        array = []
        tmp_input = []
        if current_height> self.max_blocks():
            raise Http404()
        block_info = Blocks.objects.filter(height=current_height)
        for block in block_info:
            if len(block.merkle_root.split('\'')) > 1:
                merkle_root = block.merkle_root.split('\'')[1]
            else:
                merkle_root = block.merkle_root
            array.append([
                {'height': block.height},
                {'datetime': datetime.datetime.fromtimestamp(int(block.timestamp)).strftime('%Y/%m/%d, %H:%M:%S')},
                {'version': block.version},
                {'number_of_transactions': block.number_of_transactions},
                {'block_hash': block.block_hash},
                {'version': block.version},
                {'merkle': merkle_root},
                {'nonce': block.nonce},
                {'previous_block_hash': block.previous_block_hash},
                {'tx_number': block.number_of_transactions},
                {'prev_block': int(block.height) - 1},
                {'next_block': int(block.height) + 1},
            ])

        inputs = Inputs.objects.filter(block_hash=array[0][4]['block_hash'])
        for input in inputs:
            tmp_input.append([
                {'prev_output': input.prev_output},
                {'outpoint': input.outpoint},
                {'sequence': input.sequence},
                {'tx_hash': input.tx_hash},
                {'send_from': input.address_from},
                {'outputs': []},
                {'sigscript': input.sigscript}

            ])

        for index, input in enumerate(tmp_input):
            outputs = Outputs.objects.filter(tx_hash=input[3]['tx_hash'])
            amount = 0
            for output in outputs:
                amount += round(int(output.value) / 100000000)
                tmp_input[index][5]['outputs'].append([
                    {'type': 'P2PKH'},
                    {'scriptpubkey_hex': output.scriptpubkey_hex},
                    {'send_to': output.address_to},
                    {'value': float(output.value) / 100000000},
                    {'total_amount': amount},

                ])
        array.append(tmp_input)
        max_blocks = self.max_blocks()
        return array, max_blocks

    def max_blocks(self):
        return len(Blocks.objects.all())

    def tx_info(self, current_tx_hash):
        array = []
        tmp_input = []
        block_info = []

        inputs = Inputs.objects.filter(tx_hash = current_tx_hash)
        if not len(inputs):
            raise Http404()
        for input in inputs:
            tmp_input.append([
                {'prev_output': input.prev_output},
                {'outpoint': input.outpoint},
                {'sequence': input.sequence},
                {'tx_hash': input.tx_hash},
                {'send_from': input.address_from},
                {'outputs': []},
                {'sigscript': input.sigscript}

            ])


        inputs = Inputs.objects.filter(tx_hash = current_tx_hash)
        for input in inputs:
            block = Blocks.objects.filter(block_hash = input.block_hash)
            block_info = [
                {'height': block[0].height},
                {'datetime': datetime.datetime.fromtimestamp(int(block[0].timestamp)).strftime('%Y/%m/%d, %H:%M:%S')},
                {'version': block[0].version},
                {'block_hash': block[0].block_hash},
            ]

        for index, input in enumerate(tmp_input):
            outputs = Outputs.objects.filter(tx_hash=input[3]['tx_hash'])
            amount = 0
            for output in outputs:
                amount += round(int(output.value) / 100000000)
                tmp_input[index][5]['outputs'].append([
                    {'type': 'P2PKH'},
                    {'scriptpubkey_hex': output.scriptpubkey_hex},
                    {'send_to': output.address_to},
                    {'value': round(int(output.value) / 100000000)},
                    {'total_amount': amount},

                ])
        array.append(block_info)
        array.append(tmp_input)
        return array

