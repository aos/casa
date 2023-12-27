import asyncio
from contextlib import asynccontextmanager
import datetime
import os

try:
    from zoneinfo import ZoneInfo
except ModuleNotFoundError:
    from backports.zoneinfo import ZoneInfo  # ignore

from . import smartplug

from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

DT_FORMAT = "%a %b %d %Y, %I:%M:%S %p %Z"
CWD = os.path.dirname(os.path.realpath(__file__))

templates = Jinja2Templates(directory=os.path.join(CWD, "templates"))


async def root(request: Request) -> Response:
    for k, v in request.app.state.devices.items():
        try:
            await v["device"].update()
        except smartplug.SmartDeviceException:
            continue

    return templates.TemplateResponse(
        "index.html", {"request": request, "devices": request.app.state.devices}
    )


async def toggle_plug(request: Request) -> Response:
    form_data = await request.form()
    dev = form_data.get("device")

    try:
        wait_time = int(form_data.get("wait_time") or os.environ.get("WAIT_TIME", 5))
    except ValueError:
        wait_time = 5

    asyncio.create_task(
        smartplug.toggle_plug_wait(
            request.app.state.devices[dev]["device"],
            wait_time,
        )
    )

    request.app.state.devices[dev]["last_run"] = datetime.datetime.now(
        tz=ZoneInfo("America/New_York")
    ).strftime(DT_FORMAT)

    return RedirectResponse("/", status_code=303)


async def update_devices(request: Request) -> Response:
    devs = await discover(request.app)
    request.app.state.devices = devs

    return RedirectResponse("/", status_code=303)


async def discover(app):
    devs = await smartplug.discover()
    return devs


@asynccontextmanager
async def lifespan(app):
    devs = await discover(app)

    # Turn off all plugs at the start
    for k, v in devs.items():
        await smartplug.change_plug_state(v["device"], smartplug.PlugState.OFF)
        await v["device"].update()

    app.state.devices = devs
    yield


routes = [
    Route("/", root),
    Route("/toggle", toggle_plug, methods=["POST"]),
    Route("/update", update_devices, methods=["POST"]),
    Mount(
        "/static", app=StaticFiles(directory=os.path.join(CWD, "static")), name="static"
    ),
]
