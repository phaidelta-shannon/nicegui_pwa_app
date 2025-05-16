# api/index.py
from main import ui

# Vercel Python functions must expose a `handler` function
handler = ui.server  # This exposes your FastAPI server
