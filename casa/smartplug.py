import asyncio
from enum import Enum
import os
from logging import Logger

from kasa import Discover, SmartPlug
from kasa.exceptions import SmartDeviceException

import yaml

import utils

LAST_RUNS_DIR = "./last_runs"


class PlugState(Enum):
    OFF = 0
    ON = 1


async def discover() -> dict:
    try:
        found_devs = await Discover.discover(on_discovered=lambda d: d.update())

        if found_devs:
            return {
                f"{d.alias}": {
                    "last_run": 0,
                    "device": d,
                }
                for _, d in found_devs.items()
            }
        else:
            return {}
    except SmartDeviceException:
        return {}


async def toggle_plug_wait(plug: SmartPlug, min: int):
    if min <= 0:
        return

    try:
        if plug.is_on:
            await plug.turn_off()
            await plug.update()
            await asyncio.sleep(min * 60)
            await plug.turn_on()
        else:
            await plug.turn_on()
            await plug.update()
            await asyncio.sleep(min * 60)
            await plug.turn_off()

        await plug.update()
    except SmartDeviceException:
        return


async def change_plug_state(plug: SmartPlug, state: PlugState):
    if state.ON:
        await plug.turn_off()
    else:
        await plug.turn_on()


async def init(logger: Logger, devs: dict, schedule_fn: str):
    logger.info("discovering devices...")
    await discover(devs)

    with open(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), schedule_fn), "r"
    ) as f:
        dev_schedule = yaml.load(f, Loader=yaml.Loader)
        logger.info("loaded schedule from YAML")

        for ds in dev_schedule:
            if devs.get(ds["name"]):
                devs[ds["name"]]["schedule"] = ds["schedule"]

        update_last_runs(devs)


def update_last_runs(logger: Logger, devs: dict):
    logger.info("updating last runs")

    for k, v in devs.items():
        mac = utils.clean_mac(v.get("mac"))
        if os.path.exists(os.path.join(LAST_RUNS_DIR, mac)):
            v["last_run"] = os.path.getmtime(os.path.join(LAST_RUNS_DIR, mac))
