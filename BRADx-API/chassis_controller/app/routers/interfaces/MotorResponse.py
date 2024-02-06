from pydantic import BaseModel, Field

class MotorResponse(BaseModel):
    """
    Motor Response model
    """
    @staticmethod
    def parse(message, response):
        if ("?ver" in message):
            version = response
            return "v"+version[8]+"."+version[9]+"."+version[10]
        elif ("?pos" in message):
            return response.strip("\r").split(",")[-1]
        elif ("home" in message):
            if (response != ""):
                return "succeeded"
            else:
                return "failed"
        elif ("mabs" in message):
            if (response != ""):
                return "succeeded"
            else:
                return "failed"

    submodule_id: int = Field(..., description="Submodule ID for the motor board")
    module_id: int = Field(..., description="Module ID for the motor board")
    duration_us: int = Field(..., description="Time response was returned after request was sent in microseconds")
    message: str = Field(..., description="Request message sent to the controller")
    response: str = Field(..., description="Response message received from the controller")
    value: str = Field(..., description="Get/Set value")