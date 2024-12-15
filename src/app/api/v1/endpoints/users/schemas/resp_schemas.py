from typing import Optional

from src.app.api.core.schemas.resp_schemas import BaseResp


class MeResp(BaseResp):
    uuid: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: str
