"""
Exceções personalizadas para a aplicação.
Centraliza o tratamento de erros específicos do negócio.
"""


class CorretorRedacaoException(Exception):
    """Exceção base para todos os erros da aplicação."""
    pass


class IAException(CorretorRedacaoException):
    """Erros relacionados aos serviços de IA."""
    pass


class VectorStoreException(CorretorRedacaoException):
    """Erros relacionados ao armazenamento vetorial."""
    pass


class ReportException(CorretorRedacaoException):
    """Erros relacionados à geração de relatórios."""
    pass


class DriveException(CorretorRedacaoException):
    """Erros relacionados ao Google Drive."""
    pass


class ValidationException(CorretorRedacaoException):
    """Erros de validação de dados."""
    pass


class ConfigurationException(CorretorRedacaoException):
    """Erros de configuração da aplicação."""
    pass
