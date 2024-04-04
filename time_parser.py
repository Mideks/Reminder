from datetime import datetime
from typing import Optional

import dateparser.search
import rutimeparser


def time_parser(text: str) -> Optional[datetime]:
    """Function trying to get date from text"""
    result = dateparser.search.search_dates(text, languages=("ru",))
    if not result:
        # second try with another module
        result = rutimeparser.parse(result)

    if result:
        return result[0][1]
    return None
