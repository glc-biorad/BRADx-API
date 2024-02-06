from pydantic import BaseModel, Field

class ChassisResponse(BaseModel):
    """
    Chassis Response model
    """
    @staticmethod
    def parse(response):
        if ("," in response):
            return "succeeded"
        elif (response[-2:] == 'ff'):
            version = response
            return "v"+version[0]+"."+version[1]+"."+version[2]
        else:
            if (response != ""):
                return "succeeded"
            else:
                return "failed"    

    submodule_id: int = Field(..., description="Submodule ID for the Chassis board")
    module_id: int = Field(..., description="Module ID for the Chassis board")
    duration_us: int = Field(..., description="Time response was returned after request was sent in microseconds")
    message: str = Field(..., description="Request message sent to the controller")
    response: str = Field(..., description="Response message received from the controller")
    value: str = Field(..., description="Get/Set value")