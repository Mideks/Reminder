from typing import Optional

from pydantic import BaseModel


class StateData(BaseModel):
    selected_remind_group_id: Optional[int] = None