import sys
import time
from app.controllers.migration_controller import MigrationController
from app.controllers.obfuscation_controller import ObfuscationController
from app.controllers.structure_controller import StructureController
from core.logger import setup_logging
from core.config import prod_db, homolog_db, pg_bin_path


def exibir_menu():
    print("\n" + "=" * 60)
    print("🛠️  Bem-vindo ao Sistema de Migração e Ofuscação de Dados")
    print("=" * 60)
    print("Este sistema facilita a migração de dados entre bancos PostgreSQL")
    print("e permite ofuscar dados sensíveis para proteger informações pessoais.")
    print("\nDica: use a opção '-v' ou '--verbose' para ativar o modo verbose e ver logs detalhados.")
    print("\nEscolha uma das opções abaixo:")
    print("1️⃣  Migração Geral (Drop, Create, Insert e Ofuscação)")
    print("2️⃣  Apenas Inserção de Dados")
    print("3️⃣  Somente Ofuscar Dados")
    print("4️⃣  Migração sem Ofuscação (Drop, Create e Insert)")
    print("=" * 60)


def main():
    verbose = "-v" in sys.argv or "--verbose" in sys.argv

    exibir_menu()
    opcao = input("Digite o número da opção desejada: ").strip()

    logger = setup_logging()
    migration_controller = MigrationController(prod_db, homolog_db, pg_bin_path, logger)
    obfuscation_controller = ObfuscationController(homolog_db, logger)
    structure_controller = StructureController(prod_db, homolog_db, pg_bin_path, logger)

    start_time = time.time()

    if opcao == "1":
        print("\nIniciando Migração Geral...")
        structure_controller.drop_and_recreate_homolog_db()
        migration_controller.run_migration()
        obfuscation_controller.run_obfuscation()
    elif opcao == "2":
        quantidade = input("Digite a quantidade de dados a serem inseridos: ").strip()
        print(f"\nInserindo {quantidade} registros...")
        migration_controller.run_migration(quantidade)
    elif opcao == "3":
        print("\nIniciando Ofuscação de Dados...")
        obfuscation_controller.run_obfuscation()
    elif opcao == "4":
        print("\nIniciando Migração sem Ofuscação...")
        structure_controller.drop_and_recreate_homolog_db()
        migration_controller.run_migration()
    else:
        print("\n❌ Opção inválida. Encerrando o programa.")
        return

    end_time = time.time()
    elapsed_time = end_time - start_time

    if verbose:
        mins, secs = divmod(int(elapsed_time), 60)
        print(f"\n⏱️  Tempo total de execução: {mins} minuto(s) e {secs} segundo(s)")


if __name__ == "__main__":
    main()
