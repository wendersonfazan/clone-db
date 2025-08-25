# Backup Homolog CTI

Este projeto é utilizado para gerenciar e processar dumps de banco de dados.

Ainda é um WIP ( Work In Progress )

## Estrutura do Projeto

- `main.py`: Script principal para processar os dumps.
- `logs/`: Diretório contendo logs de execução.
- `requirements.txt`: Lista de dependências do projeto.
- `.env`: Arquivo de configuração para variáveis de ambiente.
- `app/`: Diretório contendo os módulos do projeto.
- `core/`: Diretório contendo a lógica central do projeto.
- `estrutura-Final.sql`: O Arquivo que contém a estrutura do banco que será usada para criar a base de Homologação
- `estrutura.sql`: Arquivo que será gerado com a nova estrutura do banco de dados

## Pré-requisitos

Certifique-se de ter:

O Python instalado em sua máquina **Python 3**.

- Este projeto utiliza as dependências listadas no arquivo `requirements.txt`.

O **postgres 17** instalado na máquina

- vai precisar do cominho para o arquivo bin/pgdump.exe

## Como Iniciar o Projeto

1. Clone este repositório:

```bash
git clone <URL_DO_REPOSITORIO>
cd backup-homolog-cti
```

2. Crie um ambiente virtual e ative-o diferente no Windows:

- 🐧 Linux ou 🍏 MacOS:

```bash
python -m venv venv
source venv/bin/activate
```

- 🪟 Windows:

```bash
venv\Scripts\activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Configure o arquivo `.env`:
   - Copie o arquivo de exemplo:

```bash
cp .env.example .env  # No Windows: copy .env.example .env
```

- Abra o arquivo `.env` e faça as alterações necessárias, como configurar as credenciais do banco de dados. Exemplo:

> 🟠 **Cuidado:** Certifique-se de não compartilhar o arquivo `.env` publicamente, pois ele pode conter informações sensíveis, como credenciais de acesso.

> 🔴 **Cuidado:** Quando alterar os acessos tenha certeza do que está fazendo.

```.env
DB_HOST=localhost
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_NAME=nome_do_banco
```

## Como Usar o Script `main.py`

O Arquivo com a estrutura do banco de dados que será usado se chama: **estrutura-Final.sql**

1. Execute o script para iniciar a importação:

```bash
python main.py
```

2. Os logs de execução serão gerados no diretório `logs/`.

3. Verifique os resultados processados conforme necessário.
