
# Version: 2.0.0
from fastapi import APIRouter, HTTPException, Query
from chassis_controller.app.routers.interfaces.utils import convert_distance_str_to_steps
from chassis_controller.app.config.BRADx_config import *

from .interfaces.utils import (
    BRADXRequest,
    BRADxBusPacket,
    BRADxBusPacketType,
    rand_request_id,
)

from chassis_controller.app.routers.interfaces.BRADxBus import bradx_bus_timed_exchange


router = APIRouter(
    prefix="/led",
    tags=["LED"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

# Subsystem ID when accessed through the chassis/bus module
READER_SUBSYSTEM_ID = 0x03

@router.get("/version", response_model=dict, tags=["LED"])
async def get_version():
    """
    Returns the version info loaded onto the LED board
    """
    id = READER_LED
    # Build the request message and packet
    message = BRADXRequest(READER_BUS_ADDR[id], rand_request_id(), "?ver", [])
    req = BRADxBusPacket(
        READER_SUBSYSTEM_ID, id, message.raw, 25, BRADxBusPacketType.REQUEST
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
        version = pkt.data
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": READER_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": message.raw.strip(),
        "response": "v"+version[8]+"."+version[9]+"."+version[10]
    }

@router.post("/on/", response_model=dict, tags=["LED"])
async def led_channel_on(channel: LEDChannelIDs = Query(description="LED Channel ID"),
    intensity: int = Query(description="LED Intensity (%)")
    ):
    """Turn on the LED Channel
    \n
    Parameters:\n
        - channel (LEDChannelIDs): id for the LED\n
        - intensity (int): LED intensity (%)\n
    Returns:\n
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (str): '0' on Success and '1' on Error
    """
    id = READER_LED
    # Convert the intensity from percent to a value between 0 and 1000
    intensity = intensity * 10
    if intensity > LED_MAX_INTENSITY:
        raise HTTPException(status_code=422, detail="Unprocessable entity, provided intensity is larger than the maximum allowed value.")
    # Build the request message and packet
    message = BRADXRequest(READER_BUS_ADDR[id], rand_request_id(), "set", [str(channel.value), str(intensity)])
    req = BRADxBusPacket(READER_SUBSYSTEM_ID, id, message.raw, 20, BRADxBusPacketType.REQUEST)
    # Send the request and get the response
    response = -1
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
        response = 0
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": READER_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": message.raw.strip(),
        "response": str(response),
    }

@router.post("/off/", response_model=dict, tags=["LED"])
async def led_channel_off(channel: LEDChannelIDs = Query(description="LED Channel ID")):
    """Turn off the LED Channel
    \n
    Parameters:\n
        - channel (LEDChannelIDs): id for the LED channel\n
    Returns:\n
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (str): '0' on Success and '1' on Error
        """
    # Build the request message and packet
    id = READER_LED
    message = BRADXRequest(READER_BUS_ADDR[id], rand_request_id(), "off", [str(channel.value)])
    req = BRADxBusPacket(READER_SUBSYSTEM_ID, id, message.raw, 20, BRADxBusPacketType.REQUEST)
    # Send the request and get the response
    response = -1
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
        response = 0
    except ValueError as e:
        response = -1
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": READER_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": message.raw.strip(),
        "response": str(response)
    }


