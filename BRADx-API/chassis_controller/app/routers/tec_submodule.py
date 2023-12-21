
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
    prefix="/tec",
    tags=["TEC"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

# Subsystem ID when accessed through the chassis/bus module
READER_SUBSYSTEM_ID = 0x03

@router.get("/meerstetter/{id}")
async def get_object_temperature(id: MeerstetterIDs):
    """Returns the current temp of the heater in degrees Celsius"""
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[id]
    address = meerstetter_address_dict[id]
    if id not in list(meerstetter_ids_dict.values()):
        raise HTTPException(
            status_code=500, detail=f"Meerstetter at ID {id} not available"
        )
    # Build the request/response packet
    pkt = MeerstetterBusPacket(
        MeerstetterBusPacketType.GET_PARAMETER, 
        address=MEERSTETTER_BUS_ADDR[id],
        sequence= rand_request_id(),
        parameter="Object Temperature"
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await meerstetter_bus_timed_exchange(pkt)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": READER_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": pkt.raw_packet,
        "response": pkt.data,
    }

@router.post("/meerstetter/{id}")
async def set_object_temperature(
    id: int,
    setpoint: int = Query(description="Heater Setpoint"),
):
    """Set the Meersetter Setpoint"""
    if id not in [      
        READER_OEM_HEATER_FRONT_1,
        READER_OEM_HEATER_FRONT_2,
        READER_OEM_HEATER_REAR_1, 
        READER_OEM_HEATER_REAR_2  
    ]:
        raise HTTPException(
            status_code=500, detail=f"Meerstetter at ID {id} not available"
        )
    # Build the request/response packet
    pkt = MeerstetterBusPacket(
        MeerstetterBusPacketType.SET_PARAMETER, 
        address=MEERSTETTER_BUS_ADDR[id],
        sequence= rand_request_id(),
        parameter="Target Object Temp (Set)",
        value=setpoint
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await meerstetter_bus_timed_exchange(pkt)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": READER_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": pkt.raw_packet,
        "response": pkt.data,
    }

@router.post("/meerstetter/reset/{id}")
async def reset(
    id: int
):
    """Reset the Heater Channel"""
    if id not in [      
        READER_OEM_HEATER_FRONT_1,
        READER_OEM_HEATER_FRONT_2,
        READER_OEM_HEATER_REAR_1, 
        READER_OEM_HEATER_REAR_2  
    ]:
        raise HTTPException(
            status_code=500, detail=f"Meerstetter at ID {id} not available"
        )
    # Build the request/response packet
    pkt = MeerstetterBusPacket(
        MeerstetterBusPacketType.SYS_RESET, 
        address=MEERSTETTER_BUS_ADDR[id],
        sequence= rand_request_id(),
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await meerstetter_bus_timed_exchange(pkt)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": READER_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": pkt.raw_packet,
        "response": pkt.data,
    }


