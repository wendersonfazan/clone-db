import hashlib
import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

def is_valid_date(date):
    if isinstance(date, (datetime.date, datetime.datetime)):
        return True
    try:
        datetime.datetime.strptime(str(date), '%Y-%m-%d')
        return True
    except (ValueError, TypeError):
        return False


def fake_md5(value):
    return hashlib.md5(str(value).encode()).hexdigest()

def encrypt_password(password: str) -> str:
    key = b'ctiCti2025123321'  # 16 bytes
    iv = b'1233215202itCitc'   # 16 bytes
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(password.encode(), AES.block_size)
    encrypted = cipher.encrypt(padded_data)
    return base64.b64encode(encrypted).decode()


# Estados (Brasil e alguns EUA)
estados = {
    1: "AC", 2: "AL", 3: "AM", 4: "AP", 5: "BA", 6: "CE", 7: "DF", 8: "ES", 9: "GO",
    10: "MA", 11: "MG", 12: "MS", 13: "MT", 14: "PA", 15: "PB", 16: "PE", 17: "PI",
    18: "PR", 19: "RJ", 20: "RN", 21: "RO", 22: "RR", 23: "RS", 24: "SC", 25: "SE",
    26: "SP", 27: "TO", 29: "NY", 30: "NH", 31: "AR", 32: "FL"
}

parentescos = [
    "pai", "mãe",
    "irmão", "irmã",
    "tio", "tia",
    "avô", "avó",
    "primo", "prima",
    "amigo", "amiga"
]

ddds = [
    11, 12, 13, 14, 15, 16, 17, 18, 19,
    21, 22, 24, 27, 28,
    31, 32, 33, 34, 35, 37, 38,
    41, 42, 43, 44, 45, 46,
    47, 48, 49,
    51, 53, 54, 55,
    61, 62, 63, 64,
    65, 66, 67,
    68, 69,
    71, 73, 74, 75, 77, 79,
    81, 82, 83, 84, 85, 86, 87, 88, 89,
    91, 92, 93, 94, 95, 96, 97, 98, 99
]

instalacao_nome = ['Ponto A', 'Ponto B', 'False']

equipamentos = [''] + [f'Modelo: TZ {i * 100}' for i in range(1, 61)]
