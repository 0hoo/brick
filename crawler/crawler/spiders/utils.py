from typing import AnyStr, Any
import requests
import logging

import scrapy

logger = logging.getLogger()

def xpath_get(response: scrapy.http.Response, paths: Any) -> AnyStr:
    if isinstance(paths, str):
        paths = [paths]
    for p in paths:
        x = response.xpath(p).extract()
        if len(x) > 0 and x[0].strip():
            return x[0].strip()
    return ''


def xpath_get_price(selector, path: AnyStr) -> AnyStr:
    x = selector.xpath(path).extract()
    if len(x) > 0 and x[0].strip():
        x = x[0].strip()
        return x[4:].replace(',', '')
    return None

def post_message_to_telegram_bot(message):
    try:
        response = requests.post(url='https://api.telegram.org/bot323285846:AAFDNtQvqAc2vGW8MbHoA3hUQxiY1P_qzzU/sendMessage', data={'chat_id':-187896080, 'text':message}).json()
    except Exception as e:
        logger.info("Error on posting messages to the telegram bot - " + e)
