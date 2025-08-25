from faker import Faker
from core.utils import ddds, parentescos, estados, instalacao_nome, equipamentos, encrypt_password
from core.utils import fake_md5

fake = Faker("pt_BR")


def generate_tb_example_data(row):
    id = row[0]
    return [
        f"fake.city()[:40]", fake.street_address(), fake.postcode(),
        id
    ]

