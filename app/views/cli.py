def ask_migration():
    resp = input("Importar estrutura e dados de [92mPRODUÇÃO[0m para [92mHOMOLOGAÇÃO[0m? (S/N): ").upper()
    return resp == "S"

def ask_obfuscation():
    resp = input("Deseja ofuscar os dados em homologação? (S/N): ").upper()
    return resp == "S"
