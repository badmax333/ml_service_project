# import whisper
# import os
# import tempfile
# from pathlib import Path
# from typing import Optional
# from src.config import settings


# _models = {}

# def get_whisper_model(model_size: str = "base"):
#     """Ленивая загрузка модели Whisper"""
#     if model_size not in _models:
#         _models[model_size] = whisper.load_model(model_size)
#     return _models[model_size]

# def transcribe_audio_file(audio_path: str, model_size: str = "base") -> dict:
#     """
#     Транскрибирует аудиофайл с помощью Whisper
    
#     Args:
#         audio_path: путь к аудиофайлу
#         model_size: размер модели (tiny, base, small)
    
#     Returns:
#         dict: {"text": "...", "language": "...", "duration": ...}
#     """
#     model = get_whisper_model(model_size)
#     result = model.transcribe(audio_path)
    
#     return {
#         "text": result["text"],
#         "language": result["language"],
#         "duration": result.get("segments", [{}])[-1].get("end", 0) if result.get("segments") else 0
#     }

# def get_price_for_model(model_size: str) -> int:
#     """Возвращает цену за транскрибацию для модели"""
#     prices = {
#         "tiny": 5,
#         "base": 15,
#         "small": 30
#     }
#     return prices.get(model_size, 10)

# def get_available_models() -> list:
#     """Возвращает список доступных моделей с их ценами"""
#     return [
#         {"size": "tiny", "name": "Whisper Tiny", "price": get_price_for_model("tiny"), "description": "Быстрая, но менее точная"},
#         {"size": "base", "name": "Whisper Base", "price": get_price_for_model("base"), "description": "Средняя скорость и точность"},
#         {"size": "small", "name": "Whisper Small", "price": get_price_for_model("small"), "description": "Медленная, но самая точная"}
#     ]


import whisper
import os
import tempfile
from pathlib import Path
from typing import Optional
from src.config import settings

# Загрузка моделей при старте (кэшируются)
_models = {}

def get_whisper_model(model_size: str = "base"):
    """Ленивая загрузка модели Whisper"""
    if model_size not in _models:
        _models[model_size] = whisper.load_model(model_size)
    return _models[model_size]

def transcribe_audio_file(audio_path: str, model_size: str = "base") -> dict:
    """
    Транскрибирует аудиофайл с помощью Whisper
    
    Args:
        audio_path: путь к аудиофайлу
        model_size: размер модели (tiny, base, small)
    
    Returns:
        dict: {"text": "...", "language": "...", "duration": ...}
    """
    model = get_whisper_model(model_size)
    result = model.transcribe(audio_path)
    
    # Вычисляем длительность из последнего сегмента
    duration = 0
    if result.get("segments") and len(result["segments"]) > 0:
        duration = result["segments"][-1].get("end", 0)
    
    return {
        "text": result["text"],
        "language": result["language"],
        "duration": duration
    }

def get_price_for_model(model_size: str) -> int:
    """Возвращает цену за транскрибацию для модели"""
    prices = {
        "tiny": 5,
        "base": 15,
        "small": 30
    }
    return prices.get(model_size, 10)

def get_available_models() -> list:
    """Возвращает список доступных моделей с их ценами"""
    return [
        {"size": "tiny", "name": "Whisper Tiny", "price": get_price_for_model("tiny"), "description": "Быстрая, но менее точная"},
        {"size": "base", "name": "Whisper Base", "price": get_price_for_model("base"), "description": "Средняя скорость и точность"},
        {"size": "small", "name": "Whisper Small", "price": get_price_for_model("small"), "description": "Медленная, но самая точная"}
    ]