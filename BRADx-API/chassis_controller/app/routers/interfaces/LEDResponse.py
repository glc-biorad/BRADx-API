from pydantic import BaseModel, Field

class LEDResponse(BaseModel):
    """
    LED Response model
    """
    @staticmethod
    def parse(response):
        _ = response.strip("\r").split(",")
        if (len(_) == 4):
            return str(int(str(response).strip("\r").split(",")[-1])/10)    
        else:
            if (response != ""):
                return "succeeded"
            else:
                return "failed"

    submodule_id: int = Field(..., description="Submodule ID for the LED")
    module_id: int = Field(..., description="Module ID for the LED")
    duration_us: int = Field(..., description="Time response was returned after request was sent in microseconds")
    message: str = Field(..., description="Request message sent to the controller")
    response: str = Field(..., description="Response message received from the controller")
    value: str = Field(..., description="Get/Set value")