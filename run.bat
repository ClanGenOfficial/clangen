@echo off

uv sync || ( pause & exit /b )
uv run main.py || ( pause & exit /b )