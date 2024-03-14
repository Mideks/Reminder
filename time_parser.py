from datetime import datetime
from typing import Optional

"""
Ожидает время в формате dd/mm/yy HH:MM
"""
def time_parser(time: str, format: str = "%d/%m/%y %H:%M") -> Optional[datetime]:
    try:
        return datetime.strptime(time, format)
    except ValueError:
        return None
