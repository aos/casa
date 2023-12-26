import logging
import os

# import apscheduler
from starlette.applications import Starlette
import uvicorn

import routes


logger = logging.getLogger(__name__)
logging.basicConfig(
    format="[%(lineno)s - %(funcName)s] %(message)s", level=logging.INFO
)

SCHEDULE_FN = "./devices.yaml"


if __name__ == "__main__":
    debug = os.environ.get("DEBUG", True)

    try:
        port = int(os.environ.get("PORT", 8000))
    except ValueError:
        port = 8000

    app = Starlette(debug=debug, routes=routes.routes, lifespan=routes.lifespan)
    uvicorn.run(app, host="0.0.0.0", port=port)
