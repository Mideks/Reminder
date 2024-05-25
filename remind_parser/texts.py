from datetime import datetime
from typing import Optional

import dateparser.search
import rutimeparser


def parse_time(text: str) -> Optional[datetime]:
    """Function trying to get date from text"""
    result = dateparser.search.search_dates(text, languages=("ru",))
    if result:
        return result[0][1]
    else:
        # second try with another module
        result = rutimeparser.parse(text)
        if isinstance(result, datetime):
            return result
        else:
            return None


def parse_text(text: str) -> str:
    """Function trying to get text without time from text"""
    result = dateparser.search.search_dates(text, languages=("ru",))
    if result:
        return text.replace(result[0][0], '')

    return rutimeparser.get_clear_text(text)
