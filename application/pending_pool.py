from django.db import IntegrityError
from .models import Pendings


class PendingPool:

    def __init__(self, tx):
        self.tx = tx

    def submit_tx(self):
        try:
            pendings = Pendings(raw_tx=self.tx)
            pendings.save()
        except IntegrityError:
            return False
        return True
