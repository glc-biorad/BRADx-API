from pydantic import BaseModel, Field

class MeerstetterResponse(BaseModel):
    """
    Meerstetter Response model
    """
    @staticmethod
    def parse(message, response):
        if ("?ver" in message):
            version = response
            return "v"+version[8]+"."+version[9]+"."+version[10]
        else:
            if (response != ""):
                return "succeeded"
            else:
                return "failed"

    submodule_id: int = Field(..., description="Submodule ID for the Meerstetter TEC board")
    module_id: int = Field(..., description="Module ID for the Meerstetter TEC board")
    duration_us: int = Field(..., description="Time response was returned after request was sent in microseconds")
    message: str = Field(..., description="Request message sent to the controller")
    response: str = Field(..., description="Response message received from the controller")
    value: str = Field(..., description="Get/Set value")