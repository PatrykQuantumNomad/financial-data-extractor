"""
Run FastAPI server.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""
from app import create_app
from fastapi import FastAPI

application: FastAPI = create_app()
if __name__ == "__main__":
    import uvicorn

    settings = application.state.settings
    uvicorn.run(
        "run:application",
        reload=True,
        host=settings.host,
        port=settings.port,
        log_level=settings.server_log_level,
        log_config="logging.json",
        use_colors=True,
    )
