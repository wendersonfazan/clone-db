from core.data_generators import generate_tb_example_data

OBFUSCATION_TABLES = [
    {
        "table": "example",
        "select": "SELECT * FROM exemple",
        "update": """
            UPDATE exemple SET
                column_1=%s, column_2=%s, column_3=%s
            WHERE id=%s
        """,
        "generate": generate_tb_example_data
    },
]
