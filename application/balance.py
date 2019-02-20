import json
from django.db import connection

class Balance:
    def __init__(self):
        pass

    def calculate_balance(self, sender_address):
        with connection.cursor() as cursor:
            cursor.execute("SELECT amount FROM application_utxo WHERE address = %s", [sender_address])
            row = cursor.fetchall()
        if row:
            balance = 0
            for amount in row:
                balance += int(amount[0])
            return balance
        return 0