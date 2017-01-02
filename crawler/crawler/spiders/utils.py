from typing import AnyStr, Any
import scrapy


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
