"""CodeCraft Academy server entrypoint.

Keep application construction in app.create_app so tests, workers and WSGI
servers can import the same factory without starting a development server.
"""

import os

from app import create_app

application = create_app(os.getenv("FLASK_ENV", "development"))

if __name__ == "__main__":
    application.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )
