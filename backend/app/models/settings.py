from pydantic import BaseModel, ConfigDict, StrictBool


class UserSettings(BaseModel):
    courier_arrival_sms: StrictBool = False
    nearby_cart_alerts: StrictBool = False
    member_direct_chat_alerts: StrictBool = False


class UserSettingsUpdate(UserSettings):
    model_config = ConfigDict(extra="forbid")