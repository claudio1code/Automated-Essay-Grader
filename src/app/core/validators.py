"""
Validadores de dados da aplicação.
Centraliza as regras de validação de entrada.
"""

import os
import re
from typing import List, Optional
from .exceptions import ValidationException


class FileValidator:
    """Validador para operações com arquivos."""
    
    @staticmethod
    def validate_image_file(file_path: str) -> bool:
        """Valida se o arquivo é uma imagem válida."""
        if not os.path.exists(file_path):
            raise ValidationException(f"Arquivo não encontrado: {file_path}")
        
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext not in valid_extensions:
            raise ValidationException(
                f"Extensão de arquivo inválida: {file_ext}. "
                f"Use: {', '.join(valid_extensions)}"
            )
        
        return True
    
    @staticmethod
    def validate_file_size(file_path: str, max_size_mb: int = 10) -> bool:
        """Valida o tamanho máximo do arquivo em MB."""
        if not os.path.exists(file_path):
            raise ValidationException(f"Arquivo não encontrado: {file_path}")
        
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        if file_size_mb > max_size_mb:
            raise ValidationException(
                f"Arquivo muito grande: {file_size_mb:.2f}MB. "
                f"Tamanho máximo permitido: {max_size_mb}MB"
            )
        
        return True


class TextValidator:
    """Validador para operações com texto."""
    
    @staticmethod
    def validate_theme(theme: str) -> bool:
        """Valida o tema da redação."""
        if not theme or not theme.strip():
            raise ValidationException("O tema da redação não pode estar vazio")
        
        theme = theme.strip()
        if len(theme) < 5:
            raise ValidationException("O tema deve ter pelo menos 5 caracteres")
        
        if len(theme) > 200:
            raise ValidationException("O tema deve ter no máximo 200 caracteres")
        
        return True
    
    @staticmethod
    def validate_student_name(name: str) -> bool:
        """Valida o nome do aluno."""
        if not name or not name.strip():
            raise ValidationException("O nome do aluno não pode estar vazio")
        
        name = name.strip()
        if len(name) < 3:
            raise ValidationException("O nome deve ter pelo menos 3 caracteres")
        
        if len(name) > 100:
            raise ValidationException("O nome deve ter no máximo 100 caracteres")
        
        # Verifica se contém apenas letras e espaços
        if not re.match(r'^[a-zA-ZÀ-ÿ\s]+$', name):
            raise ValidationException("O nome deve conter apenas letras e espaços")
        
        return True


class DriveValidator:
    """Validador para operações com Google Drive."""
    
    @staticmethod
    def validate_folder_id(folder_id: str) -> bool:
        """Valida o ID da pasta do Google Drive."""
        if not folder_id or not folder_id.strip():
            raise ValidationException("O ID da pasta não pode estar vazio")
        
        folder_id = folder_id.strip()
        
        # Remove URL se fornecida
        if "drive.google.com" in folder_id:
            match = re.search(r"folders/([a-zA-Z0-9-_]+)", folder_id)
            if match:
                folder_id = match.group(1)
            else:
                raise ValidationException("URL da pasta do Drive inválida")
        
        # Valida formato do ID
        if not re.match(r'^[a-zA-Z0-9-_]+$', folder_id):
            raise ValidationException("ID da pasta do Drive inválido")
        
        return True
