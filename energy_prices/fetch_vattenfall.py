import datetime
from decimal import Decimal

from dateutil import parser as date_parser
import requests

from django.utils import timezone
from filecache import filecache

from energy_prices.categories import PriceCategories, calculate_categories
from energy_prices.models import Price

hour_in_seconds = 60 * 60


@filecache(8 * hour_in_seconds)
def get_hourly_prices(date: datetime.date | str) -> dict:
    if isinstance(date, datetime.date):
        date = date.isoformat()
    print(f'Fetching prices from Vattenfallen for {date}')
    url = f'https://www.vattenfall.fi/api/price/spot/{date}/{date}?lang=fi'
    # ic(date, url)
    result = requests.get(url)
    return result.json()

# @filecache(1 * hour_in_seconds)
def update_hourly_prices(date=datetime.date.today()) -> dict:
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
    calculate_categories(result)
    return result


def get_current_price(dt: datetime = timezone.now()) -> (PriceCategories, Decimal):
    previous_even_hour = timezone.datetime(dt.year, dt.month, dt.day, dt.hour, 0)
    prices = update_hourly_prices()
    price_now, category = prices[previous_even_hour]
    # ic(prices, previous_even_hour, price_now, category)
    return (category, price_now)
