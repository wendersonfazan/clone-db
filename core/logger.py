import logging
import sys
import time
import os
import datetime
from colorama import init, Fore, Style

init(autoreset=True)
start_time = time.time()

class TimeFormatter(logging.Formatter):
    def format(self, record):
        elapsed_time = time.time() - start_time
        record.elapsed = f"{elapsed_time:.2f}s"
        return super().format(record)

class ColorFormatter(TimeFormatter):
    def format(self, record):
        return super().format(record)

def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    data_hora = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    log_file_path = os.path.join(log_dir, f"process_{data_hora}.log")

    file_handler = logging.FileHandler(log_file_path, mode="a", encoding="utf-8")
    file_formatter = TimeFormatter("%(asctime)s - [%(elapsed)s] - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = ColorFormatter("%(asctime)s - [%(elapsed)s] - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=getattr(logging, log_level, logging.INFO), handlers=[
        file_handler, console_handler])
    logging.info(f"Inicio em: {datetime.datetime.now()}")

    return logging.getLogger()
