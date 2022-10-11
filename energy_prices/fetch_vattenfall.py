import datetime
from decimal import Decimal
from enum import Enum

from dateutil import parser as date_parser
import requests
from typing import Optional

import pytz
import logging

from django.utils import timezone
from icecream import ic
from filecache import filecache

from energy_prices.models import Price

hour_in_seconds = 60 * 60

THRESHOLD_CHEAP = 0.009
THRESHOLD_EXPENSIVE = 0.02


class PriceCategories(Enum):
    CHEAP = 'C'
    NORMAL = 'N'
    EXPENSIVE = 'E'

    @staticmethod
    def categorize(price: float | Decimal) -> "PriceCategories":
        if price <= THRESHOLD_CHEAP:
            return PriceCategories.CHEAP
        if price >= THRESHOLD_EXPENSIVE:
            return PriceCategories.EXPENSIVE
        return PriceCategories.NORMAL


@filecache(8 * hour_in_seconds)
def get_hourly_prices(date: datetime.date | str) -> dict:
    if isinstance(date, datetime.date):
        date = date.isoformat()
    print(f'Fetching prices from Vattenfallen for {date}')
    url = f'https://www.vattenfall.fi/api/price/spot/{date}/{date}?lang=fi'
    ic(date, url)
    result = requests.get(url)
    return result.json()

# @filecache(8 * hour_in_seconds)
def update_hourly_prices(date=datetime.date.today()) -> list:
    print(f'Updating prices from Vattenfallen')
    prices = get_hourly_prices(date)
    # ic(prices)
    result = []
    for p in prices:
        start_time: datetime = pytz.timezone('UTC').localize(date_parser.parse(p['timeStamp']))
        divider = 100 if p['unit'] == 'snt/kWh' else 1
        price, created = Price.objects.update_or_create(
            start_time=start_time, defaults=dict(price=Decimal(p['value'])/divider)
        )
        # print(f'Price {price.price} starting at {price.start_time}, created: {created}')
        category = PriceCategories.categorize(price.price)
        result.append((price.start_time, Decimal(price.price), category))
    ic(result)
    return result


def get_current_price(dt: datetime = timezone.now()) -> Optional[float]:
    """
    # >>> type(get_current_price('FI'))
    <class 'float'>
    """
    previous_even_hour = timezone.datetime(dt.year, dt.month, dt.day, dt.hour, 0)  # Miksi UTC?
    ic(previous_even_hour)
    return None
