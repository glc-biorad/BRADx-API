
# Version: Test
from re import S
from urllib import response
from fastapi import APIRouter, HTTPException, Query
from chassis_controller.app.routers.interfaces.utils import convert_distance_str_to_steps
from chassis_controller.app.config.BRADx_config import *
from chassis_controller.app.routers.interfaces.MeerstetterResponse import MeerstetterResponse

from .interfaces.utils import (
    BRADXRequest,
    BRADxBusPacket,
    BRADxBusPacketType,
    rand_request_id,
)

from chassis_controller.app.routers.interfaces.utils_meerstetter import (
    MeerstetterBusPacket, 
    MeerstetterBusPacketType,
    TEC_DEVICE_STATUSES,
    MEERSTETTER_ERRORS,
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

# NOTE: TEC_PARAMETERS that are taken from the TEC commands doc are located in /routers/interface/utils_meerstetter.py

@router.get("/object-temperature/", response_model=MeerstetterResponse, tags=["TEC"])
async def get_object_temperature(heater: MeerstetterIDs):
    """
    Returns the current temp of the object in degrees Celsius
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
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        response = str(pkt.data)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
        response = "None"
    return MeerstetterResponse(submodule_id=READER_SUBSYSTEM_ID,
                               module_id=id,
                               duration_us=elapsed,
                               message=str(pkt.raw_packet),
                               response=str(pkt.data),
                               value=MeerstetterResponse.parse(str(pkt.raw_packet), str(pkt.data)))

@router.post("/object-temperature/")
async def set_object_temperature(
    heater: MeerstetterIDs,
    setpoint: float):
    """
    Set the target object temperature for the selected heater\n
    \n
    Parameters:\n
        - heater (MeerstetterIDs): heater to be used\n
        - setpoint (float): target object temperature for the heater\n
    Returns:
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
    address = meerstetter_address_dict[id]
    if id not in list(meerstetter_ids_dict.values()):
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
        "response": str(pkt.data),
    }

@router.get("/sink-temperature/", response_model=dict, tags=["TEC"])
async def get_sink_temperature(heater: MeerstetterIDs):
    """
    Returns the current temp of the sink in degrees Celsius
    \n
    Parameters:\n
        - heater (MeerstetterIDs): name of the heater to be checked\n
    Returns:\n
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data (Sink Temperature [Celsius])
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Sink Temperature"
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
        "response": str(pkt.data),
    }

@router.get("/target-object-temperature/", response_model=dict, tags=["TEC"])
async def get_target_object_temperature(heater: MeerstetterIDs):
    """
    Returns the current target temperature of the object in degrees Celsius
    \n
    Parameters:\n
        - heater (MeerstetterIDs): name of the heater to be checked\n
    Returns:\n
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data (Target Object Temperature [Celsius])
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Target Object Temperature"
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
        "response": str(pkt.data),
    }

@router.get("/actual-output-current/", response_model=dict, tags=["TEC"])
async def get_actual_output_current(heater: MeerstetterIDs):
    """
    Returns the current actual output current in Amperes
    \n
    Parameters:\n
        - heater (MeerstetterIDs): name of the heater to be checked\n
    Returns:\n
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data (Actual Output Current [A])
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Actual Output Current"
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
        "response": str(pkt.data),
    }

@router.get("/actual-output-voltage/", response_model=dict, tags=["TEC"])
async def get_actual_output_voltage(heater: MeerstetterIDs):
    """
    Returns the current actual output voltage in Volts
    \n
    Parameters:\n
        - heater (MeerstetterIDs): name of the heater to be checked\n
    Returns:\n
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data (Actual Output Voltage [V])
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Actual Output Voltage"
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
        "response": str(pkt.data),
    }

@router.get("/relative-cooling-power/", response_model=dict, tags=["TEC"])
async def get_relative_cooling_power(heater: MeerstetterIDs):
    """
    Returns the relative cooling power of the fan for the selected heater
    \n
    Parameters:\n
        - heater (MeerstetterIDs): name of the heater to be checked\n
    Returns:\n
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data (Relative Cooling Power [%])
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Relative Cooling Power"
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
        "response": str(pkt.data),
    }

@router.get("/actual-fan-speed/", response_model=dict, tags=["TEC"])
async def get_actual_fan_Speed(heater: MeerstetterIDs):
    """
    Returns the actual fan speed for the selected heater's fan
    \n
    Parameters:\n
        - heater (MeerstetterIDs): name of the heater to be checked\n
    Returns:\n
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data (Actual Fan Speed [rpm])
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Actual Fan Speed"
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
        "response": str(pkt.data),
    }

@router.get("/target-fan-temperature/", response_model=dict, tags=["TEC"])
async def get_fan_target_temperature(heater: MeerstetterIDs):
    """
    Returns the target temperature for the selected heater's fan
    \n
    Parameters:\n
        - heater (MeerstetterIDs): name of the heater to be checked\n
    Returns:\n
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data (Target Fan Speed (C))
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Target Temperature"
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
        "response": str(pkt.data),
    }

@router.post("/target-fan-temperature/")
async def set_fan_target_temperature(
    heater: MeerstetterIDs,
    setpoint: float):
    """
    Set the target fan temperature for the selected heater\n
    \n
    Parameters:\n
        - heater (MeerstetterIDs): heater to be used\n
        - setpoint (float): target fan temperature for the heater\n
    Returns:
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
    address = meerstetter_address_dict[id]
    if id not in list(meerstetter_ids_dict.values()):
        raise HTTPException(
            status_code=500, detail=f"Meerstetter at ID {id} not available"
        )
    # Build the request/response packet
    pkt = MeerstetterBusPacket(
        MeerstetterBusPacketType.SET_PARAMETER, 
        address=MEERSTETTER_BUS_ADDR[id],
        sequence= rand_request_id(),
        parameter="Target Temperature",
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
        "response": str(pkt.data),
    }

@router.get("/current-error-threshold/", response_model=dict, tags=["TEC"])
async def get_current_error_threshold(heater: MeerstetterIDs):
    """
    Returns the current error threshold for the selected heater
    \n
    Parameters:\n
        - heater (MeerstetterIDs): name of the heater to be checked\n
    Returns:\n
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data (Current Error Threshold [A])
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Current Error Threshold"
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
        "response": str(pkt.data),
    }

@router.post("/current-error-threshold/")
async def set_current_error_threshold(
    heater: MeerstetterIDs,
    setpoint: float):
    """
    Set the current error threshold for the selected heater\n
    \n
    Parameters:\n
        - heater (MeerstetterIDs): heater to be used\n
        - setpoint (float): current error threshold [A] for the heater\n
    Returns:
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data (Current Error Threshold [A])
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
    address = meerstetter_address_dict[id]
    if id not in list(meerstetter_ids_dict.values()):
        raise HTTPException(
            status_code=500, detail=f"Meerstetter at ID {id} not available"
        )
    # Build the request/response packet
    pkt = MeerstetterBusPacket(
        MeerstetterBusPacketType.SET_PARAMETER, 
        address=MEERSTETTER_BUS_ADDR[id],
        sequence= rand_request_id(),
        parameter="Current Error Threshold",
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
        "response": str(pkt.data),
    }

@router.get("/voltage-error-threshold/", response_model=dict, tags=["TEC"])
async def get_voltage_error_threshold(heater: MeerstetterIDs):
    """
    Returns the voltage error threshold for the selected heater
    \n
    Parameters:\n
        - heater (MeerstetterIDs): name of the heater to be checked\n
    Returns:\n
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data (Voltage Error Threshold [V])
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Voltage Error Threshold"
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
        "response": str(pkt.data),
    }

@router.post("/voltage-error-threshold/")
async def set_voltage_error_threshold(
    heater: MeerstetterIDs,
    setpoint: float):
    """
    Set the voltage error threshold for the selected heater\n
    \n
    Parameters:\n
        - heater (MeerstetterIDs): heater to be used\n
        - setpoint (float): voltage error threshold [V] for the heater\n
    Returns:
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data (Voltage Error Threshold [V])
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
    address = meerstetter_address_dict[id]
    if id not in list(meerstetter_ids_dict.values()):
        raise HTTPException(
            status_code=500, detail=f"Meerstetter at ID {id} not available"
        )
    # Build the request/response packet
    pkt = MeerstetterBusPacket(
        MeerstetterBusPacketType.SET_PARAMETER, 
        address=MEERSTETTER_BUS_ADDR[id],
        sequence= rand_request_id(),
        parameter="Voltage Error Threshold",
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
        "response": str(pkt.data),
    }

@router.get("/object-upper-error-threshold/", response_model=dict, tags=["TEC"])
async def get_object_upper_error_threshold(heater: MeerstetterIDs):
    """
    Returns the object upper error threshold for the selected heater
    \n
    Parameters:\n
        - heater (MeerstetterIDs): name of the heater to be checked\n
    Returns:\n
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data (Current Error Threshold [A])
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Object Upper Error Threshold"
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
        "response": str(pkt.data),
    }

@router.get("/object-lower-error-threshold/", response_model=dict, tags=["TEC"])
async def get_object_lower_error_threshold(heater: MeerstetterIDs):
    """
    Returns the object lower error threshold for the selected heater
    \n
    Parameters:\n
        - heater (MeerstetterIDs): name of the heater to be checked\n
    Returns:\n
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data (Current Error Threshold [A])
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Object Lower Error Threshold"
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
        "response": str(pkt.data),
    }

@router.get("/sink-upper-error-threshold/", response_model=dict, tags=["TEC"])
async def get_sink_upper_error_threshold(heater: MeerstetterIDs):
    """
    Returns the sink upper error threshold for the selected heater
    \n
    Parameters:\n
        - heater (MeerstetterIDs): name of the heater to be checked\n
    Returns:\n
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data (Current Error Threshold [A])
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Sink Upper Error Threshold"
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
        "response": str(pkt.data),
    }

@router.get("/sink-lower-error-threshold/", response_model=dict, tags=["TEC"])
async def get_sink_lower_error_threshold(heater: MeerstetterIDs):
    """
    Returns the sink lower error threshold for the selected heater
    \n
    Parameters:\n
        - heater (MeerstetterIDs): name of the heater to be checked\n
    Returns:\n
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data (Current Error Threshold [A])
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Sink Lower Error Threshold"
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
        "response": str(pkt.data),
    }

@router.get("/temperature-is-stable/", response_model=dict, tags=["TEC"])
async def get_temperature_is_stable(heater: MeerstetterIDs):
    """
    Returns the temperature is stable result for the selected heater
    \n
    Parameters:\n
        - heater (MeerstetterIDs): name of the heater to be checked\n
    Returns:\n
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data (Current Error Threshold [A])
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Temperature is Stable"
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await meerstetter_bus_timed_exchange(pkt)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    if (pkt.data == 0):
        response = "Temperature regulation is not active"
    elif (pkt.data == 1):
        response = "Is not stable"
    elif (pkt.data):
        response = "Is stable"
    return {
        "_sid": READER_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": pkt.raw_packet,
        "response": response,
    }

@router.get("/temperature-control/", response_model=dict, tags=["TEC"])
async def get_chx_output_stage_enabled(heater: MeerstetterIDs):
    """
    Returns the status of the CHx Output Stage Enabled for the selected heater
    \n
    Parameters:\n
        - heater (MeerstetterIDs): name of the heater to be checked\n
    Returns:\n
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data (Current Error Threshold [A])
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Status"
    )
    # Send the request and get the response
    response = "Off"
    try:
        pkt, elapsed = await meerstetter_bus_timed_exchange(pkt)
        response = "Off" if pkt.data == ChxOutputStageEnableIntOption.Off else "On"
    except ValueError as e:
        #response = options.get_option(-1)
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": READER_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": pkt.raw_packet,
        "response": response,
    }



@router.post("/temperature-control/")
async def set_chx_output_stage_enabled(
    heater: MeerstetterIDs,
    status: ChxOutputStageEnableStrOption):
    """
    Set the CHx Output Stage Enable for the selected heater\n
    \n
    Parameters:\n
        - heater (MeerstetterIDs): heater to be used\n
        - setpoint (float): target object temperature for the heater\n
    Returns:
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
    address = meerstetter_address_dict[id]
    if id not in list(meerstetter_ids_dict.values()):
        raise HTTPException(
            status_code=500, detail=f"Meerstetter at ID {id} not available"
        )
    # Get the int option from the str option for CHx Output Stage Enable
    status = 1 if (status == ChxOutputStageEnableStrOption.On.value) else 0
    # Build the request/response packet
    pkt = MeerstetterBusPacket(
        MeerstetterBusPacketType.SET_PARAMETER, 
        address=MEERSTETTER_BUS_ADDR[id],
        sequence= rand_request_id(),
        parameter="Status",
        value=status
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await meerstetter_bus_timed_exchange(pkt)
        response = str(pkt.data)
    except ValueError as e:
        response = -1
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": READER_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": pkt.raw_packet,
        "response": response,
    }

@router.post("/fan-control/")
async def set_chx_fan_control_enable(
    heater: MeerstetterIDs,
    status: FanControlEnableStateStrOption):
    """
    Set the CHx Fan Control for the selected heater\n
    \n
    Parameters:\n
        - heater (MeerstetterIDs): heater to be used\n
        - status (FanControlEnableStateStrOption): state of the fan\n
    Returns:
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
    address = meerstetter_address_dict[id]
    if id not in list(meerstetter_ids_dict.values()):
        raise HTTPException(
            status_code=500, detail=f"Meerstetter at ID {id} not available"
        )
    # Get the int option from the str option for CHx Fan Control State
    status = 1 if (status == FanControlEnableStateStrOption.Enabled.value) else 0
    # Build the request/response packet
    pkt = MeerstetterBusPacket(
        MeerstetterBusPacketType.SET_PARAMETER, 
        address=MEERSTETTER_BUS_ADDR[id],
        sequence= rand_request_id(),
        parameter="Fan Control Enable",
        value=status
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await meerstetter_bus_timed_exchange(pkt)
        response = str(pkt.data)
    except ValueError as e:
        response = -1
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": READER_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": pkt.raw_packet,
        "response": response,
    }

@router.get("/fan-control/")
async def get_chx_fan_control_enable(
    heater: MeerstetterIDs):
    """
    Set the CHx Fan Control for the selected heater\n
    \n
    Parameters:\n
        - heater (MeerstetterIDs): heater to be used\n
    Returns:
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Fan Control Enable"
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await meerstetter_bus_timed_exchange(pkt)
        response = str(pkt.data)
    except ValueError as e:
        response = -1
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": READER_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": pkt.raw_packet,
        "response": response,
    }

@router.get("/Kp/", response_model=dict, tags=["TEC"])
async def get_pid_Kp(heater: MeerstetterIDs):
    """
    Returns the current proportional PID value for the selected heater
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
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Kp"
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await meerstetter_bus_timed_exchange(pkt)
        response = str(pkt.data)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
        response = "None"
    return {
        "_sid": READER_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": pkt.raw_packet,
        "response": response,
    }

@router.post("/Kp/")
async def set_pid_Kp(
    heater: MeerstetterIDs,
    setpoint: float):
    """
    Set the PID proportional term for the selected heater\n
    \n
    Parameters:\n
        - heater (MeerstetterIDs): heater to be used\n
        - setpoint (float): Proportional term for the PID\n
    Returns:
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
    address = meerstetter_address_dict[id]
    if id not in list(meerstetter_ids_dict.values()):
        raise HTTPException(
            status_code=500, detail=f"Meerstetter at ID {id} not available"
        )
    # Build the request/response packet
    pkt = MeerstetterBusPacket(
        MeerstetterBusPacketType.SET_PARAMETER, 
        address=MEERSTETTER_BUS_ADDR[id],
        sequence= rand_request_id(),
        parameter="Kp",
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
        "response": str(pkt.data),
    }

@router.get("/Ti/", response_model=dict, tags=["TEC"])
async def get_pid_Ti(heater: MeerstetterIDs):
    """
    Returns the current integral PID value for the selected heater
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
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Ti"
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await meerstetter_bus_timed_exchange(pkt)
        response = str(pkt.data)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
        response = "None"
    return {
        "_sid": READER_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": pkt.raw_packet,
        "response": response,
    }

@router.post("/Ti/")
async def set_pid_Ti(
    heater: MeerstetterIDs,
    setpoint: float):
    """
    Set the PID integral term for the selected heater\n
    \n
    Parameters:\n
        - heater (MeerstetterIDs): heater to be used\n
        - setpoint (float): Integral term for the PID\n
    Returns:
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
    address = meerstetter_address_dict[id]
    if id not in list(meerstetter_ids_dict.values()):
        raise HTTPException(
            status_code=500, detail=f"Meerstetter at ID {id} not available"
        )
    # Build the request/response packet
    pkt = MeerstetterBusPacket(
        MeerstetterBusPacketType.SET_PARAMETER, 
        address=MEERSTETTER_BUS_ADDR[id],
        sequence= rand_request_id(),
        parameter="Ti",
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
        "response": str(pkt.data),
    }

@router.get("/Td/", response_model=dict, tags=["TEC"])
async def get_pid_Td(heater: MeerstetterIDs):
    """
    Returns the current derivative PID value for the selected heater
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
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Td"
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await meerstetter_bus_timed_exchange(pkt)
        response = str(pkt.data)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
        response = "None"
    return {
        "_sid": READER_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": pkt.raw_packet,
        "response": response,
    }

@router.post("/Td/")
async def set_pid_Td(
    heater: MeerstetterIDs,
    setpoint: float):
    """
    Set the PID derivative term for the selected heater\n
    \n
    Parameters:\n
        - heater (MeerstetterIDs): heater to be used\n
        - setpoint (float): Proportional term for the PID\n
    Returns:
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
    address = meerstetter_address_dict[id]
    if id not in list(meerstetter_ids_dict.values()):
        raise HTTPException(
            status_code=500, detail=f"Meerstetter at ID {id} not available"
        )
    # Build the request/response packet
    pkt = MeerstetterBusPacket(
        MeerstetterBusPacketType.SET_PARAMETER, 
        address=MEERSTETTER_BUS_ADDR[id],
        sequence= rand_request_id(),
        parameter="Td",
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
        "response": str(pkt.data),
    }

@router.get("/current-limitation/", response_model=dict, tags=["TEC"])
async def get_current_limitation(heater: MeerstetterIDs):
    """
    Returns the current current limitation value for the selected heater
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
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Current Limitation"
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await meerstetter_bus_timed_exchange(pkt)
        response = str(pkt.data)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
        response = "None"
    return {
        "_sid": READER_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": pkt.raw_packet,
        "response": response,
    }

@router.post("/current-limitation/")
async def set_current_limitation(
    heater: MeerstetterIDs,
    setpoint: float):
    """
    Set the current limitation for the selected heater\n
    \n
    Parameters:\n
        - heater (MeerstetterIDs): heater to be used\n
        - setpoint (float): Proportional term for the PID\n
    Returns:
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
    address = meerstetter_address_dict[id]
    if id not in list(meerstetter_ids_dict.values()):
        raise HTTPException(
            status_code=500, detail=f"Meerstetter at ID {id} not available"
        )
    # Build the request/response packet
    pkt = MeerstetterBusPacket(
        MeerstetterBusPacketType.SET_PARAMETER, 
        address=MEERSTETTER_BUS_ADDR[id],
        sequence= rand_request_id(),
        parameter="Current Limitation",
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
        "response": str(pkt.data),
    }

@router.get("/voltage-limitation/", response_model=dict, tags=["TEC"])
async def get_voltage_limitation(heater: MeerstetterIDs):
    """
    Returns the current voltage limitation value for the selected heater
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
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Voltage Limitation"
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await meerstetter_bus_timed_exchange(pkt)
        response = str(pkt.data)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
        response = "None"
    return {
        "_sid": READER_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": pkt.raw_packet,
        "response": response,
    }

@router.post("/voltage-limitation/")
async def set_voltage_limitation(
    heater: MeerstetterIDs,
    setpoint: float):
    """
    Set the voltage limitation for the selected heater\n
    \n
    Parameters:\n
        - heater (MeerstetterIDs): heater to be used\n
        - setpoint (float): Proportional term for the PID\n
    Returns:
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
    address = meerstetter_address_dict[id]
    if id not in list(meerstetter_ids_dict.values()):
        raise HTTPException(
            status_code=500, detail=f"Meerstetter at ID {id} not available"
        )
    # Build the request/response packet
    pkt = MeerstetterBusPacket(
        MeerstetterBusPacketType.SET_PARAMETER, 
        address=MEERSTETTER_BUS_ADDR[id],
        sequence= rand_request_id(),
        parameter="Voltage Limitation",
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
        "response": str(pkt.data),
    }

@router.get("/firmware-version/", response_model=dict, tags=["TEC"])
async def get_firmware_version(heater: MeerstetterIDs):
    """
    Returns the firmware version loaded on the TEC
    \n
    Parameters:\n
        - heater (MeerstetterIDs): name of the heater to be checked\n
    Returns:\n
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (str): deserialized data (Firmware Version)
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Firmware Version"
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
        "response": str(pkt.data)[:-2] + "." + str(pkt.data)[-2:],
    }

@router.get("/device-status/", response_model=dict, tags=["TEC"])
async def get_device_status(heater: MeerstetterIDs):
    """
    Returns the Device Status for the TEC
    \n
    Parameters:\n
        - heater (MeerstetterIDs): name of the heater to be checked\n
    Returns:\n
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (str): deserialized data (Device Status)
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Device Status"
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
        "response": TEC_DEVICE_STATUSES[pkt.data],
    }

@router.get("/device-address/", response_model=dict, tags=["TEC"])
async def get_device_address(heater: MeerstetterIDs):
    """
    Returns the Device Address for the TEC
    \n
    Parameters:\n
        - heater (MeerstetterIDs): name of the heater to be checked\n
    Returns:\n
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (str): deserialized data (Device Address)
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Device Address"
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
        "response": str(pkt.data),
    }

@router.get("/error-number/", response_model=dict, tags=["TEC"])
async def get_error_number(heater: MeerstetterIDs):
    """
    Returns the error number for the selected heater's fan
    \n
    Parameters:\n
        - heater (MeerstetterIDs): name of the heater to be checked\n
    Returns:\n
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data (Target Fan Speed (C))
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Error Number"
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
        "response": str(pkt.data),
    }

@router.get("/error-description/", response_model=dict, tags=["TEC"])
async def get_error_description(heater: MeerstetterIDs):
    """
    Returns the error number for the selected heater's fan
    \n
    Parameters:\n
        - heater (MeerstetterIDs): name of the heater to be checked\n
    Returns:\n
        - _sid (int): submodule id\n
        - _mid (int): module id\n
        - _duration_us (int): elapsed time in microseconds\n
        - message (str): raw packet\n
        - response (float): deserialized data (Target Fan Speed (C))
    """
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
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
        parameter="Error Number"
    )
    # Send the request and get the response
    resp = "-1"
    try:
        pkt, elapsed = await meerstetter_bus_timed_exchange(pkt)
        resp = MEERSTETTER_ERRORS[int(pkt.data)]
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": READER_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": pkt.raw_packet,
        "response": resp,
    }

@router.post("/meerstetter/reset/")
async def reset(
    heater: MeerstetterIDs
):
    """Reset the Heater Channel"""
    # Convert string to address
    meerstetter_ids_dict = MeerstetterIDs.get_ids(MeerstetterIDs)
    meerstetter_address_dict = MeerstetterIDs.get_addresses(MeerstetterIDs)
    id = meerstetter_ids_dict[heater]
    address = meerstetter_address_dict[id]
    if id not in list(meerstetter_ids_dict.values()):
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
        "response": str(pkt.data),
    }


