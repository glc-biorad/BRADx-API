
# Version: Test
from fastapi import APIRouter, HTTPException, Query
from chassis_controller.app.routers.interfaces.utils import convert_distance_str_to_steps
from chassis_controller.app.config.BRADx_config import *

from .interfaces.utils import (
    BRADXRequest,
    BRADxBusPacket,
    BRADxBusPacketType,
    rand_request_id,
)

from chassis_controller.app.routers.interfaces.utils_meerstetter import (
    MeerstetterBusPacket, 
    MeerstetterBusPacketType
)

from chassis_controller.app.routers.interfaces.BRADxBus import bradx_bus_timed_exchange
from chassis_controller.app.routers.interfaces.MeerstetterBus import meerstetter_bus_timed_exchange


router = APIRouter(
    prefix="/reader",
    tags=["reader"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

# Subsystem ID when accessed through the chassis/bus module
READER_SUBSYSTEM_ID = 0x03


@router.get("/axis/version/{id}")
async def get_version(id: int):
    """Returns the version info of the given axis"""
    if id not in [
        READER_X_AXIS,       
        READER_Y_AXIS,       
        READER_Z_AXIS,       
        READER_FILTER_WHEEL,  
        READER_TRAY_AB,    
        READER_TRAY_CD,     
        READER_HEATER_CA,
        READER_HEATER_CB,
        READER_HEATER_CC,
        READER_HEATER_CD,
        READER_LED
    ]:
        raise HTTPException(
            status_code=500, detail=f"Motor axis at ID {id} not available"
        )
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

@router.get("/axis/position/{id}")
async def get_status_and_position(id: int):
    """Returns the status and most recent position value of the addressed motor"""
    if id not in [
        READER_X_AXIS,       
        READER_Y_AXIS,       
        READER_Z_AXIS,       
        READER_FILTER_WHEEL,  
        READER_TRAY_AB,    
        READER_TRAY_CD,     
        READER_HEATER_CA,
        READER_HEATER_CB,
        READER_HEATER_CC,
        READER_HEATER_CD
    ]:
        raise HTTPException(
            status_code=500, detail=f"Motor axis at ID {id} not available"
        )
    # Build the request message and packet
    message = BRADXRequest(READER_BUS_ADDR[id], rand_request_id(), "?pos", [])
    req = BRADxBusPacket(
        READER_SUBSYSTEM_ID, id, message.raw, 25, BRADxBusPacketType.REQUEST
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": READER_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": message.raw.strip(),
        "response": pkt.data,
    }


@router.post("/axis/move/{id}")
async def set_axis_position(
    id: int ,
    position: int = Query(description="Axis absolute position"),
    velocity: int = Query(description="Velocity to use when moving"),
):

    if id not in [
        READER_X_AXIS,       
        READER_Y_AXIS,       
        READER_Z_AXIS,       
        READER_FILTER_WHEEL,  
        READER_TRAY_AB,    
        READER_TRAY_CD,     
        READER_HEATER_CA,
        READER_HEATER_CB,
        READER_HEATER_CC,
        READER_HEATER_CD
    ]:
        raise HTTPException(
            status_code=500, detail=f"Motor axis at ID {id} not available"
        )
    # Build the request message and packet
    message = BRADXRequest(READER_BUS_ADDR[id], rand_request_id(), "mabs", [str(position), str(velocity)])
    req = BRADxBusPacket(
        READER_SUBSYSTEM_ID, id, message.raw, 20, BRADxBusPacketType.REQUEST
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": READER_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": message.raw.strip(),
        "response": pkt.data,
    }


@router.post("/axis/home/{id}")
async def home_axis(id: int):
    """Home the axis"""
    if id not in [
        READER_X_AXIS,       
        READER_Y_AXIS,       
        READER_Z_AXIS,       
        READER_FILTER_WHEEL,  
        READER_TRAY_AB,    
        READER_TRAY_CD,     
        READER_HEATER_CA,
        READER_HEATER_CB,
        READER_HEATER_CC,
        READER_HEATER_CD 
    ]:
        raise HTTPException(
            status_code=500, detail=f"Motor axis at ID {id} not available"
        )
    # Build the request message and packet
    message = BRADXRequest(READER_BUS_ADDR[id], rand_request_id(), "home", [])
    req = BRADxBusPacket(
        READER_SUBSYSTEM_ID, id, message.raw, 20, BRADxBusPacketType.REQUEST
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": READER_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": message.raw.strip(),
        "response": pkt.data,
    }

@router.post("/axis/jog/{id}")
async def jog_axis(
    id: int,
    distance: str = Query(description="Axis jog distance and direction (units required (mm/um), sign and decimal point optional"),
    velocity: int = Query(description="Velocity to use when moving"),
):
    """Set the position of the axis"""
    if id not in [
        READER_X_AXIS,       
        READER_Y_AXIS,       
        READER_Z_AXIS,       
        READER_FILTER_WHEEL,  
        READER_TRAY_AB,    
        READER_TRAY_CD,     
        READER_HEATER_CA,
        READER_HEATER_CB,
        READER_HEATER_CC,
        READER_HEATER_CD 
    ]:
        raise HTTPException(
            status_code=500, detail=f"Motor axis at ID {id} not available"
        )

    # Convert the string to a step amount
    steps = convert_distance_str_to_steps(distance, READER_STEP_RATIO[id])

    # Build the request message and packet
    message = BRADXRequest(READER_BUS_ADDR[id], rand_request_id(), "mrel", [str(steps), str(velocity)])
    req = BRADxBusPacket(
        READER_SUBSYSTEM_ID, id, message.raw, 20, BRADxBusPacketType.REQUEST
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": READER_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": message.raw.strip(),
        "response": pkt.data,
    }


# @router.post("/led/{id}")
# async def led_channel_on(
#     id: int,
#     channel: int = Query(description="LED Channel ID"),
#     intensity: int = Query(description="LED Intensity, max 1000")
#     ):
#     """Turn on the LED Channel"""
#     if id not in [
#         READER_LED
#     ]:
#         raise HTTPException(
#             status_code=500, detail=f"LED at ID {id} not available"
#         )

#     # Build the request message and packet
#     message = BRADXRequest(READER_BUS_ADDR[READER_LED], rand_request_id(), "set", [str(channel), str(intensity)])
#     req = BRADxBusPacket(
#         READER_SUBSYSTEM_ID, id, message.raw, 20, BRADxBusPacketType.REQUEST
#     )
#     # Send the request and get the response
#     try:
#         pkt, elapsed = await bradx_bus_timed_exchange(req)
#     except ValueError as e:
#         raise HTTPException(status_code=500, detail=str(e))
#     return {
#         "_sid": READER_SUBSYSTEM_ID,
#         "_mid": id,
#         "_duration_us": elapsed,
#         "message": message.raw.strip(),
#         "response": pkt.data,
#     }

# @router.post("/led/{id}/off")
# async def led_channel_off(
#     id: int,
#     channel: int = Query(description="LED Channel ID")
#     ):
#     """Turn off the LED Channel"""
#     if id not in [
#         READER_LED
#     ]:
#         raise HTTPException(
#             status_code=500, detail=f"LED at ID {id} not available"
#         )

#     # Build the request message and packet
#     message = BRADXRequest(READER_BUS_ADDR[READER_LED], rand_request_id(), "off", [str(channel)])
#     req = BRADxBusPacket(
#         READER_SUBSYSTEM_ID, id, message.raw, 20, BRADxBusPacketType.REQUEST
#     )
#     # Send the request and get the response
#     try:
#         pkt, elapsed = await bradx_bus_timed_exchange(req)
#     except ValueError as e:
#         raise HTTPException(status_code=500, detail=str(e))
#     return {
#         "_sid": READER_SUBSYSTEM_ID,
#         "_mid": id,
#         "_duration_us": elapsed,
#         "message": message.raw.strip(),
#         "response": pkt.data,
#     }


