from dataclasses import dataclass

from src.app.application.common.services.base import BaseSvcOutEntity


@dataclass
class AppBaseDTO(BaseSvcOutEntity):
    pass
