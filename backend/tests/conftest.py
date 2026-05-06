import sys
from pathlib import Path

# Добавляем корневую папку backend в PYTHONPATH
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

print(f"✅ PYTHONPATH updated: {backend_path}")