@echo off

poetry install --no-root || ( pause & exit /b )
poetry run python main.py || ( pause & exit /b )