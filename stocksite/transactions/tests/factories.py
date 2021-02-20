from factory import DjangoModelFactory, Faker
from ..models import Transaction

class TransactionFactory(DjangoModelFactory):
    type = Faker('UserCommand')
    timestamp = Faker('1613270145482')
    server = Faker('127.0.0.1')
    transctionNum = Faker('0')
    command = Faker('BUY')
    username = Faker('oY01WVirLr')
    stockSymbol = Faker('S')
    amount = Faker('276.00')

    class Meta:
        model = Transaction