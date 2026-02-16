"""
Utilitários gerais da aplicação.
Funções auxiliares reutilizáveis.
"""

import os
import re
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from PIL import Image


class FileUtils:
    """Utilitários para manipulação de arquivos."""
    
    @staticmethod
    def ensure_directory(path: str) -> None:
        """Garante que o diretório existe."""
        os.makedirs(path, exist_ok=True)
    
    @staticmethod
    def get_unique_filename(base_path: str, extension: str = "") -> str:
        """Gera um nome de arquivo único com timestamp e UUID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}_{unique_id}"
        
        if extension and not extension.startswith('.'):
            extension = f".{extension}"
        
        return f"{filename}{extension}"
    
    @staticmethod
    def safe_filename(filename: str) -> str:
        """Remove caracteres inválidos de nomes de arquivo."""
        # Remove caracteres inválidos para Windows/Linux
        invalid_chars = r'[<>:"/\\|?*]'
        clean_name = re.sub(invalid_chars, '_', filename)
        
        # Remove espaços extras
        clean_name = re.sub(r'\s+', '_', clean_name.strip())
        
        # Limita tamanho
        if len(clean_name) > 255:
            name, ext = os.path.splitext(clean_name)
            clean_name = f"{name[:255-len(ext)]}{ext}"
        
        return clean_name


class ImageUtils:
    """Utilitários para manipulação de imagens."""
    
    @staticmethod
    def validate_and_optimize_image(image_path: str, max_size_mb: int = 5) -> str:
        """Valida e otimiza imagem se necessário."""
        try:
            with Image.open(image_path) as img:
                # Verifica tamanho
                file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
                
                if file_size_mb > max_size_mb:
                    # Reduz qualidade se for muito grande
                    output_path = FileUtils.get_unique_filename(
                        os.path.splitext(image_path)[0], 
                        os.path.splitext(image_path)[1][1:]
                    )
                    
                    # Reduz dimensões se necessário
                    max_dimension = 2048
                    if max(img.width, img.height) > max_dimension:
                        img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                    
                    # Salva com qualidade reduzida
                    img.save(output_path, optimize=True, quality=85)
                    return output_path
                
                return image_path
                
        except Exception as e:
            raise Exception(f"Erro ao processar imagem: {str(e)}")
    
    @staticmethod
    def get_image_info(image_path: str) -> Dict[str, Any]:
        """Retorna informações básicas da imagem."""
        try:
            with Image.open(image_path) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode,
                    "size_mb": os.path.getsize(image_path) / (1024 * 1024)
                }
        except Exception:
            return {}


class TextUtils:
    """Utilitários para manipulação de texto."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Limpa e normaliza texto."""
        if not text:
            return ""
        
        # Remove espaços extras
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove caracteres especiais problemáticos
        text = re.sub(r'[^\w\s\-.,!?;:()\[\]{}"\'/\\]', '', text)
        
        return text
    
    @staticmethod
    def extract_drive_id(url_or_id: str) -> Optional[str]:
        """Extrai ID de pasta do Google Drive de URL ou retorna o ID."""
        if not url_or_id:
            return None
        
        # Regex para capturar ID na URL do Drive
        match = re.search(r"folders/([a-zA-Z0-9-_]+)", url_or_id)
        if match:
            return match.group(1)
        
        # Se não for URL, assume que já é o ID
        if re.match(r'^[a-zA-Z0-9-_]+$', url_or_id):
            return url_or_id
        
        return None
    
    @staticmethod
    def format_grade(nota: int) -> str:
        """Formata nota para exibição."""
        if nota < 200:
            return f"{nota} pontos"
        return f"{nota} pontos"
    
    @staticmethod
    def get_competence_grade_color(nota: int) -> str:
        """Retorna cor baseada na nota da competência."""
        if nota >= 160:
            return "🟢"
        elif nota >= 120:
            return "🟡"
        else:
            return "🔴"
