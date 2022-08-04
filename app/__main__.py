import uvicorn
from app.settings import settings

from .database import init_db

if __name__ == '__main__':
    init_db()
    uvicorn.run(
        'app.app:app',
        host=settings.server_host,
        port=settings.server_port,
        reload=True,
    )
