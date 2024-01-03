
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
    MeerstetterBusPacketType,
    TEC_DEVICE_STATUSES,
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

@router.get("/object-temperature/", response_model=dict, tags=["TEC"])
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
    return {
        "_sid": READER_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": pkt.raw_packet,
        "response": response,
    }

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
        "response": str(pkt.data),
    }


