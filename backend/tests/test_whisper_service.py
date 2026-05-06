import pytest
from unittest.mock import MagicMock, patch

def test_get_price_for_model_and_available_models():
    from src.services.whisper_service import get_price_for_model, get_available_models
    
    assert get_price_for_model("tiny") == 5
    assert get_price_for_model("base") == 15
    assert get_price_for_model("small") == 30
    assert get_price_for_model("unknown") == 10
    
    models = get_available_models()
    assert len(models) == 3
    assert models[0]["size"] == "tiny"
    assert models[1]["size"] == "base"
    assert models[2]["size"] == "small"

@patch("src.services.whisper_service.whisper")
def test_transcribe_audio_file_duration_from_segments(mock_whisper):
    """Тест с моком whisper модели"""
    from src.services.whisper_service import transcribe_audio_file
    
    # Настраиваем мок модели
    mock_model = MagicMock()
    mock_result = {
        "text": "hello",
        "language": "en",
        "segments": [{"end": 1.0}, {"end": 2.5}]
    }
    mock_model.transcribe.return_value = mock_result
    mock_whisper.load_model.return_value = mock_model
    
    result = transcribe_audio_file("any_file.wav", model_size="base")
    
    assert result["text"] == "hello"
    assert result["language"] == "en"
    assert result["duration"] == 2.5
    mock_whisper.load_model.assert_called_once_with("base")

@patch("src.services.whisper_service.whisper")
def test_transcribe_audio_file_duration_defaults_to_zero(mock_whisper):
    """Тест когда нет сегментов"""
    from src.services.whisper_service import transcribe_audio_file
    
    mock_model = MagicMock()
    mock_result = {
        "text": "hello",
        "language": "en",
        "segments": None
    }
    mock_model.transcribe.return_value = mock_result
    mock_whisper.load_model.return_value = mock_model
    
    result = transcribe_audio_file("any_file.wav", model_size="tiny")
    
    assert result["duration"] == 0