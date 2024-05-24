from typing import Optional

from pydantic import BaseModel


class StateData(BaseModel):
    selected_remind_group_id: Optional[int] = None
    raw_reminds: Optional[list[list[str]]] = None
    selected_raw_remind: Optional[int] = None
