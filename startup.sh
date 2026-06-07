#!/bin/bash
# Railway startup: generate mock data if not present, then start API
if [ ! -f "data/chat_history.jsonl" ]; then
  echo "Generating mock data..."
  python data/generate_mock_data.py
fi
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
