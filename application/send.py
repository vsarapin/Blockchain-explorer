from .balance import Balance
from .validator import Validator
from .transaction import Transaction
from .models import Generated
from django.db import connection
import json


class Send:
    def __init__(self, from_value, to_value, amount_value, fee_value):
        self.from_value = from_value
        self.to_value = to_value
        self.amount_value = amount_value
        self.fee_value = fee_value

    def check_income_data(self):
        condition = 0

        # Check input parameters
        if condition not in {len(self.from_value) or len(self.to_value)}:
            # Check amount
            try:
                self.amount_value = int(self.amount_value)
            except ValueError:
                self.amount_value = float(self.amount_value)

            # Check fee
            try:
                self.fee_value = int(self.fee_value)
            except ValueError:
                self.fee_value = float(self.fee_value)

            validator = Validator()
            # Check addresses
            if validator.check_bc(self.from_value) and validator.check_bc(self.to_value):

                # Check that public key corresponds to sender`s address
                if self.check_sender_public_key(self.from_value):
                    # Check that there is enough coins on balance to send
                    check_balance = self.check_sender_balance()
                    if check_balance == True:

                        # Coins in satoshis
                        try:
                            self.amount_value = int(self.amount_value * 100000000)
                        except ValueError:
                            return 'Enter valid amount!'
                        try:
                            self.fee_value = int(self.fee_value * 100000000)
                        except ValueError:
                            return 'Enter valid fee!'

                        # Get neccessary input parameters from utxo to form raw transaction
                        # input_counter = self.tx_input_info()
                        input_counter, input_prev_hashes, vout, output_counter, tx_amount = self.tx_input_info()
                        # From transaction
                        transaction = Transaction(self.from_value, self.to_value, self.amount_value, self.fee_value, input_prev_hashes)
                        transaction.input_counter = input_counter
                        transaction.input_prev_hashes = input_prev_hashes
                        transaction.vout = vout
                        transaction.output_counter = output_counter
                        transaction.tx_amount = tx_amount

                        real_tx = transaction.create_transaction()
                        return real_tx

                    else:
                        return check_balance
                else:
                    return '__from__ address not in your wallet!'
            else:
                return 'Check both addresses!'

        else:
            return 'You must fill all fields!'

    def check_sender_public_key(self, sender_address):
        with connection.cursor() as cursor:
            cursor.execute("SELECT public_key FROM application_generated WHERE address = %s", [sender_address])
            row = cursor.fetchone()
        if row:
            validator = Validator()
            if validator.compareAddresses(bytes.fromhex(row[0]), sender_address):
                return True

        with connection.cursor() as cursor:
            cursor.execute("SELECT public_key FROM application_miner WHERE address = %s", [sender_address])
            row = cursor.fetchone()
        if row:
            validator = Validator()
            if validator.compareAddresses(bytes.fromhex(row[0]), sender_address):
                return True
        return False

    def check_sender_balance(self):
        if self.amount_value <= 0:
            return 'Amount can`t be 0 or less!'
        if self.fee_value <= 0:
            return 'Fee can`t be 0 or less!'

        balance = Balance()
        current_balance = balance.calculate_balance(self.from_value)
        if current_balance < self.amount_value + self.fee_value:
            return 'Not enough coins on __from__ balance!'
        else:
            return True

    def tx_input_info(self):
        total = self.amount_value + self.fee_value
        input_counter = 0
        output_counter = 1
        input_prev_hashes = []
        vout = []
        tx_amount = []

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM application_utxo WHERE address = %s", [self.from_value])
            row = cursor.fetchall()
        if row:
            for key in row:
                input_counter += 1
                input_prev_hashes.append(key[1])
                vout.append(key[3])
                try:
                    amount = int(key[4])
                except ValueError:
                    amount = float(key[4])
                amount_in_transaction = amount
                tx_amount.append(amount_in_transaction)
                amount_in_transaction -= total
                if amount_in_transaction >= 0:
                    if amount_in_transaction > 0:
                        return input_counter, input_prev_hashes, vout, output_counter + 1, tx_amount
                    if amount_in_transaction == 0:
                        return input_counter, input_prev_hashes, vout, output_counter, tx_amount
                else:
                    total -= amount
