from datetime import datetime
from typing import Optional

import dateparser.search
import rutimeparser


def time_parser(text: str) -> Optional[datetime]:
    """Function trying to get date from text"""
    result = dateparser.search.search_dates(text, languages=("ru",))
    if not result:
        # second try with another module
        result = rutimeparser.parse(text)

    if result:
        return result[0][1]
    return None


def text_parser(text: str) -> str:
    """Function trying to get text without time from text"""
    result = dateparser.search.search_dates(text, languages=("ru",))
    if result:
        return text.replace(result[0][0], '')

    return rutimeparser.get_clear_text(text)
