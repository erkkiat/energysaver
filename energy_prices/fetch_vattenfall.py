import datetime
from decimal import Decimal
from typing import Union

from cachetools.func import ttl_cache
from dateutil import parser as date_parser
import requests

from django.utils import timezone
from filecache import filecache
from icecream import ic

from energy_prices.categories import PriceCategories, calculate_categories
from energy_prices.message import messages
from energy_prices.models import Price

hour_in_seconds = 60 * 60


@ttl_cache(ttl=8 * hour_in_seconds)
def get_hourly_prices(date: Union[datetime.date, str]) -> dict:
    if isinstance(date, datetime.date):
        date = date.isoformat()
    messages.message(f'Fetching prices from Vattenfallen for {date}')
    url = f'https://www.vattenfall.fi/api/price/spot/{date}/{date}?lang=fi'
    # ic(date, url)
    result = requests.get(url)
    data = result.json()
    if result.status_code >= 400 or len(data) < 24:
        messages.message(f'There seems to be a connection issue with Vattenfallen: '
                         f'status code {result.status_code}, {len(data)} hourly entries')
    return result.json()

# @filecache(4 * hour_in_seconds)
def update_hourly_prices(date: datetime.date = None) -> dict:
    date = date or datetime.date.today()  # If not specified as parameter
    messages.message(f'Updating prices from Vattenfallen on {date}')
    prices = get_hourly_prices(date)
    # ic(prices)
    result = dict()
    for p in prices:
        start_time: datetime = date_parser.parse(p['timeStamp'])
        divider = 100 if p['unit'] == 'snt/kWh' else 1
        price, created = Price.objects.update_or_create(
            start_time=start_time, defaults=dict(price=round(Decimal(p['value'])/divider, 3))
        )
        # print(f'Price {price.price} starting at {price.start_time}, created: {created}')
        category = PriceCategories.categorize(price.price)
        result[price.start_time] = (round(Decimal(price.price), 3), category)
    # ic(result)
    return calculate_categories(date, result)


def get_current_price(dt: datetime.datetime = None) -> (PriceCategories, Decimal):
    try:
        if not dt:
            dt = timezone.now()
        previous_even_hour = timezone.datetime(dt.year, dt.month, dt.day, dt.hour, 0)
        prices = update_hourly_prices(dt.date())
        # ic(prices)
        p = [
            (date.hour, f'{round(price, 2)} €/kWh', category.name)
            for date, (price, category) in prices.items()
        ]
        ic(p)
        price_now, category = prices[previous_even_hour]
        # ic(previous_even_hour, price_now, category)
        return (category, price_now)
    except Exception as e:
        messages.message(f'Cannot fetch prices currently, retrying in 1 hour: {e}')
        get_hourly_prices.cache_clear()
        return (PriceCategories.CHEAP, 0.0) if dt.hour < 7 else (PriceCategories.EXPENSIVE, 9999)