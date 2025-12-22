import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Configura e retorna uma instância de logger padronizada para a aplicação.

    Args:
        name (str): O nome do logger, geralmente passado como __name__.

    Returns:
        logging.Logger: O objeto logger configurado.
    """
    logger = logging.getLogger(name)

    # Se o logger já possui handlers configurados, retorna para evitar duplicação
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    # Configuração do handler para saída no console (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Formato da mensagem de log: Data | Nível | Módulo | Mensagem
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
