
# Version: 2.0.0
# for now change version number manually
# xx.yy.zz
# xx - Major update / feature addition
# yy - Minor update / enhancement to existing commands
# zz - Bug fix
FASTAPI_VERSION     = "2.0.0"

# Meerstetter vid (Vender ID), pid (Product ID) and ser (Serial Number) for the board
MEERSTETTER_VID = "0403"
MEERSTETTER_PID = "6001"
MEERSTETTER_SER = "AQ034U3RA"

# Subsystem ID when accessed through the chassis/bus module
CHASSIS_SUBSYSTEM_ID = 0x00

# Subsystem ID when accessed through the chassis/bus module
PREP_DECK_SUBSYSTEM_ID = 0x02

# Subsystem ID when accessed through the chassis/bus module
READER_SUBSYSTEM_ID = 0x03

# Reader Subsystem module IDs when accessed through the chassis/bus module
READER_X_AXIS               = 0x01
READER_Y_AXIS               = 0x02
READER_Z_AXIS               = 0x03
READER_FILTER_WHEEL         = 0x04
READER_LED                  = 0x05
READER_TRAY_AB              = 0x06
READER_TRAY_CD              = 0x07
READER_HEATER_CA            = 0x08
READER_HEATER_CB            = 0x09
READER_HEATER_CC            = 0x0A
READER_HEATER_CD            = 0x0B
READER_OEM_HEATER_FRONT_1   = 0x0C
READER_OEM_HEATER_FRONT_2   = 0x0D
READER_OEM_HEATER_REAR_1    = 0x0E
READER_OEM_HEATER_REAR_2    = 0x0F
READER_IMAGER_CAMERA        = 0x10

# Pipettor Subsystem module IDs when accessed through the chassis/bus module

PIPETTOR_X_MOTOR = 0x01
PIPETTOR_Y_MOTOR = 0x02
PIPETTOR_Z_MOTOR = 0x03
PIPETTOR_DRIP_MOTOR = 0x04
PIPETTOR_AIR_SYSTEM = 0x05
PIPETTOR_CAMERA = 0x06
PIPETTOR_PIPETTOR = 0x07

# Prep Deck Subsystem module IDs when accessed through the chassis/bus module
PREP_PLATE_CHILLER  = 0x01
PREP_HEATER_SHAKER  = 0x02
PREP_THERMOCYCLER_1 = 0x03
PREP_THERMOCYCLER_2 = 0x04
PREP_MARLOW         = 0x05
PREP_MAG_SEPARATOR  = 0x06
PREP_HEATER_RNA_1   = 0x07
PREP_HEATER_RNA_2   = 0x08
PREP_HEATER_RNA_3   = 0x09
PREP_HEATER_RNA_4   = 0x0A

TEST = 0x7



#  Reader RS485 Bus -2 Addresses
READER_BUS_ADDR = {
                    READER_X_AXIS               : 0x01,
                    READER_Y_AXIS               : 0x02,
                    READER_Z_AXIS               : 0x03,
                    READER_FILTER_WHEEL         : 0x04,
                    READER_LED                  : 0x05,
                    READER_TRAY_AB              : 0x06,
                    READER_TRAY_CD              : 0x07,
                    READER_HEATER_CA            : 0x08,
                    READER_HEATER_CB            : 0x09,
                    READER_HEATER_CC            : 0x0A,
                    READER_HEATER_CD            : 0x0B,                    
                    READER_OEM_HEATER_FRONT_1   : 0x0C,
                    READER_OEM_HEATER_FRONT_2   : 0x0D,
                    READER_OEM_HEATER_REAR_1    : 0x0E,
                    READER_OEM_HEATER_REAR_2    : 0x0F

}

#  Pipettor RS485 Bus - 1 Addresses
PIPETTOR_BUS_ADDR = {
                    PIPETTOR_X_MOTOR    : 0x01,
                    PIPETTOR_Y_MOTOR    : 0x02,
                    PIPETTOR_Z_MOTOR    : 0x03,
                    PIPETTOR_DRIP_MOTOR : 0x04,
                    PIPETTOR_AIR_SYSTEM : 0x05,
                    PREP_MAG_SEPARATOR  : 0x06,
                    TEST: 0x7

}

# LED Max Intensity
LED_MAX_INTENSITY = 1000

from enum import Enum
from tkinter import OFF 
class PipettorGantryAxisOptions(str, Enum):
    x = 'X'
    y = 'Y'
    z = 'Z'
    drip_plate = "Drip Plate"
    def get_id(self, id):
        print(id)
        print('ttt')
        ids = {
            self.x: PIPETTOR_X_MOTOR,
            self.y: PIPETTOR_Y_MOTOR,
            self.z: PIPETTOR_Z_MOTOR,
            self.drip_plate: PIPETTOR_DRIP_MOTOR
            }
        return ids[id]
    def get_address(self, id):
        addresses = PIPETTOR_BUS_ADDR
        return addresses[self.get_ids(self, id)]

#  Pipettor RS485 Bus Addresses
PREP_BUS_ADDR = {
                    PREP_PLATE_CHILLER  : 0x01,
                    PREP_HEATER_SHAKER  : 0x02,
                    PREP_THERMOCYCLER_1 : 0x03,
                    PREP_THERMOCYCLER_2 : 0x04,
                    PREP_MARLOW         : 0x05,
                    PREP_MAG_SEPARATOR  : 0x06,
                    PREP_HEATER_RNA_1   : 0x07,
                    PREP_HEATER_RNA_2   : 0x08,
                    PREP_HEATER_RNA_3   : 0x09,
                    PREP_HEATER_RNA_4   : 0x0A

}

#  Meerstetter RS232 Bus Addresses
# TODO: Look into setting this to agree with the CDP 2.0 convention (A: 1, B: 2, C: 3, D: 4)
MEERSTETTER_BUS_ADDR = {
    READER_OEM_HEATER_FRONT_1 : 0x04,
    READER_OEM_HEATER_FRONT_2 : 0x03,
    READER_OEM_HEATER_REAR_1  : 0x02, 
    READER_OEM_HEATER_REAR_2  : 0x01

}

from enum import Enum 
class MeerstetterIDs(str, Enum):
    heater_a = "Heater A"
    heater_b = "Heater B"
    heater_c = "Heater C"
    heater_d = "Heater D"
    def get_ids(self):
        ids = {
            self.heater_a: READER_OEM_HEATER_REAR_2,
            self.heater_b: READER_OEM_HEATER_REAR_1,
            self.heater_c: READER_OEM_HEATER_FRONT_2,
            self.heater_d: READER_OEM_HEATER_FRONT_1,
            }
        return ids
    def get_addresses(self):
        addresses = MEERSTETTER_BUS_ADDR
        return addresses
    
class LEDChannelIDs(str, Enum):
    one = '1'
    two = '2'
    three = '3'
    four = '4'
    five = '5'
    six = '6'
    
class ChxOutputStageEnableIntOption(int, Enum):
    Off = 0
    On = 1
    
class ChxOutputStageEnableStrOption(str, Enum):
    Off = "Off"
    On = "On"
    
class FanControlEnableStateStrOption(str, Enum):
    Disabled = "Disabled",
    Enabled = "Enabled"
    
class FanControlEnableStateIntOption(int, Enum):
    Disabled = 0,
    Enabled = 1

#  Step to um conversion values for the Pipettor motors
PIPETTOR_STEP_RATIO = { PIPETTOR_X_MOTOR    : 100,
                        PIPETTOR_Y_MOTOR    : 100,
                        PIPETTOR_Z_MOTOR    : 100,
                        PIPETTOR_DRIP_MOTOR : 100

}

#  Step to um conversion values for the Reader motors
READER_STEP_RATIO = {   READER_X_AXIS       :  100,     
                        READER_Y_AXIS       :  100,     
                        READER_Z_AXIS       :  100,     
                        READER_FILTER_WHEEL : 100, 
                        READER_TRAY_AB      : 100,   
                        READER_TRAY_CD      : 100,    

}