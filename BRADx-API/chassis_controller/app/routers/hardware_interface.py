
# Version: Test
from fastapi import APIRouter, Query, HTTPException

from chassis_controller.app.routers.interfaces.utils import BRADxBusPacket, BRADxBusPacketType
from chassis_controller.app.routers.interfaces.BRADxBus import bradx_bus_timed_exchange
from chassis_controller.app.config.BRADx_config import *

router = APIRouter(
    prefix="",
    tags=["Hardware Interface"],
    dependencies=[],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal error"},
    },
)


@router.get("/")
async def root():
    return {"message": "BRADx System Hardware Interface"}

@router.get("/serial-number/", response_model=dict, tags=["Hardware Interface"])
async def get_serial_number():
    """
    Returns the Serial Number for the TECs RS485-to-USB converter
    \n
    Parameters:\n
        - heater (MeerstetterIDs): name of the heater to be checked\n
    Returns:\n
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data (Object Temperature)
    """
    # Get the Serial Number from the Config file
    ser = MEERSTETTER_SER
    return {
        "_sid": 0,
        "_mid": 0,
        "_duration_us": 0,
        "message": "",
        "response": ser,
    }
