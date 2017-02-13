# -*- coding: utf-8 -*-
import re
import dateparser


def string_only(text):
    return re.sub('<[^>]*>', '', text)


def datetime_only(text):
    FMT = '%d/%m/%Y'

    if not text:
        return None

    result = re.findall(
        '(\d{2}/\d{2}/\d{4})*', text)


    if result:
        date = result[0]

        return date

    else:
        data = dateparser.parse(
            text, settings={'DATE_ORDER': 'DMY'})
        if data:
            return data.strftime(FMT)
        else:
            return None
