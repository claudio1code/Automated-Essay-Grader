"""
Testes para validadores da aplicação.
"""

import pytest
import tempfile
import os
from src.app.core.validators import FileValidator, TextValidator, DriveValidator
from src.app.core.exceptions import ValidationException


class TestFileValidator:
    """Testes para validador de arquivos."""
    
    def test_validate_image_file_success(self):
        """Testa validação de imagem válida."""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            tmp.write(b"fake image content")
            tmp_path = tmp.name
        
        try:
            assert FileValidator.validate_image_file(tmp_path) == True
        finally:
            os.unlink(tmp_path)
    
    def test_validate_image_file_not_found(self):
        """Testa validação de arquivo inexistente."""
        with pytest.raises(ValidationException, match="Arquivo não encontrado"):
            FileValidator.validate_image_file("nonexistent.jpg")
    
    def test_validate_image_file_invalid_extension(self):
        """Testa validação de extensão inválida."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b"text content")
            tmp_path = tmp.name
        
        try:
            with pytest.raises(ValidationException, match="Extensão de arquivo inválida"):
                FileValidator.validate_image_file(tmp_path)
        finally:
            os.unlink(tmp_path)
    
    def test_validate_file_size_success(self):
        """Testa validação de tamanho válido."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"x" * 1000)  # 1KB
            tmp_path = tmp.name
        
        try:
            assert FileValidator.validate_file_size(tmp_path, max_size_mb=10) == True
        finally:
            os.unlink(tmp_path)
    
    def test_validate_file_size_too_large(self):
        """Testa validação de arquivo muito grande."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"x" * (11 * 1024 * 1024))  # 11MB
            tmp_path = tmp.name
        
        try:
            with pytest.raises(ValidationException, match="Arquivo muito grande"):
                FileValidator.validate_file_size(tmp_path, max_size_mb=10)
        finally:
            os.unlink(tmp_path)


class TestTextValidator:
    """Testes para validador de texto."""
    
    def test_validate_theme_success(self):
        """Testa validação de tema válido."""
        assert TextValidator.validate_theme("Tema válido para redação") == True
    
    def test_validate_theme_empty(self):
        """Testa validação de tema vazio."""
        with pytest.raises(ValidationException, match="O tema da redação não pode estar vazio"):
            TextValidator.validate_theme("")
    
    def test_validate_theme_too_short(self):
        """Testa validação de tema muito curto."""
        with pytest.raises(ValidationException, match="O tema deve ter pelo menos 5 caracteres"):
            TextValidator.validate_theme("abc")
    
    def test_validate_theme_too_long(self):
        """Testa validação de tema muito longo."""
        long_theme = "a" * 201
        with pytest.raises(ValidationException, match="O tema deve ter no máximo 200 caracteres"):
            TextValidator.validate_theme(long_theme)
    
    def test_validate_student_name_success(self):
        """Testa validação de nome válido."""
        assert TextValidator.validate_student_name("João Silva") == True
    
    def test_validate_student_name_empty(self):
        """Testa validação de nome vazio."""
        with pytest.raises(ValidationException, match="O nome do aluno não pode estar vazio"):
            TextValidator.validate_student_name("")
    
    def test_validate_student_name_too_short(self):
        """Testa validação de nome muito curto."""
        with pytest.raises(ValidationException, match="O nome deve ter pelo menos 3 caracteres"):
            TextValidator.validate_student_name("ab")
    
    def test_validate_student_name_invalid_chars(self):
        """Testa validação de nome com caracteres inválidos."""
        with pytest.raises(ValidationException, match="O nome deve conter apenas letras e espaços"):
            TextValidator.validate_student_name("João123")


class TestDriveValidator:
    """Testes para validador do Google Drive."""
    
    def test_validate_folder_id_success(self):
        """Testa validação de ID válido."""
        assert DriveValidator.validate_folder_id("1abc123def456") == True
    
    def test_validate_folder_id_empty(self):
        """Testa validação de ID vazio."""
        with pytest.raises(ValidationException, match="O ID da pasta não pode estar vazio"):
            DriveValidator.validate_folder_id("")
    
    def test_validate_folder_id_url_success(self):
        """Testa validação de URL do Drive."""
        url = "https://drive.google.com/drive/folders/1abc123def456"
        assert DriveValidator.validate_folder_id(url) == True
    
    def test_validate_folder_id_invalid_url(self):
        """Testa validação de URL inválida."""
        url = "https://drive.google.com/drive/folders/"
        with pytest.raises(ValidationException, match="URL da pasta do Drive inválida"):
            DriveValidator.validate_folder_id(url)
    
    def test_validate_folder_id_invalid_format(self):
        """Testa validação de formato inválido."""
        with pytest.raises(ValidationException, match="ID da pasta do Drive inválido"):
            DriveValidator.validate_folder_id("invalid@id")


if __name__ == "__main__":
    pytest.main([__file__])
