import datetime
from decimal import Decimal
from typing import Union

from dateutil import parser as date_parser
import requests

from django.utils import timezone
from filecache import filecache
from icecream import ic

from energy_prices.categories import PriceCategories, calculate_categories
from energy_prices.message import messages
from energy_prices.models import Price

hour_in_seconds = 60 * 60


@filecache(8 * hour_in_seconds)
def get_hourly_prices(date: Union[datetime.date, str]) -> dict:
    if isinstance(date, datetime.date):
        date = date.isoformat()
    print(f'Fetching prices from Vattenfallen for {date}')
    url = f'https://www.vattenfall.fi/api/price/spot/{date}/{date}?lang=fi'
    # ic(date, url)
    result = requests.get(url)
    data = result.json()
    if result.status_code >= 400 or len(data) < 300:
        messages.message('There seems to be a connection issue with Vattenfallen')
    return result.json()

# @filecache(8 * hour_in_seconds)
def update_hourly_prices(date: datetime.datetime = None) -> dict:
    date = date or datetime.date.today()  # If not specified as parameter
    print(f'Updating prices from Vattenfallen on {date}')
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


def get_current_price(dt: datetime = None) -> (PriceCategories, Decimal):
    if not dt:
        dt = timezone.now()
    previous_even_hour = timezone.datetime(dt.year, dt.month, dt.day, dt.hour, 0)
    prices = update_hourly_prices()
    ic(prices)
    price_now, category = prices[previous_even_hour]
    ic(previous_even_hour, price_now, category)
    return (category, price_now)
