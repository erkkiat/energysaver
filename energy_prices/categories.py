import datetime
import os
from collections import Counter
from decimal import Decimal
from enum import Enum
from typing import Union

from icecream import ic

from energy_prices.message import messages

THRESHOLD_EXTREMELY_CHEAP = round(Decimal(os.environ.get('THRESHOLD_EXTREMELY_CHEAP',0.02)), 3)
THRESHOLD_CHEAP = round(Decimal(os.environ.get('THRESHOLD_CHEAP',0.06)), 3)
THRESHOLD_EXPENSIVE = round(Decimal(os.environ.get('THRESHOLD_EXPENSIVE', 0.14)), 3)
MINIMUM_HEATING_HOURS = int(os.environ.get('MINIMUM_HEATING_HOURS', 6))


class PriceCategories(Enum):
    EXTREMELY_CHEAP = 1
    CHEAP = 2
    NORMAL = 3
    EXPENSIVE = 4
    FORCED = 5  # In case there are not enough cheap hours in the day to keep the house warm

    @staticmethod
    def categorize(price: Union[float, Decimal]) -> "PriceCategories":
        if price <= THRESHOLD_EXTREMELY_CHEAP:
            return PriceCategories.EXTREMELY_CHEAP
        if price <= THRESHOLD_CHEAP:
            return PriceCategories.CHEAP
        if price >= THRESHOLD_EXPENSIVE:
            return PriceCategories.EXPENSIVE
        return PriceCategories.NORMAL


def fill_out_default_categories(date: datetime.date, prices: dict) -> dict:
    # If price data is not available, fill out a cheap night and an expensive day
    if len(prices) == 24:
        return prices

    messages.message(f'There is a problem fetching price data for date {date}, reverting to default scheme')

    year = date.year
    month = date.month
    day = date.day

    def cheap_hour(hour: int) -> bool:
        return 1 <= hour <= 6

    for hour in range(0,23):
        category = PriceCategories.CHEAP if cheap_hour(hour) else PriceCategories.EXPENSIVE
        price = 0 if cheap_hour(hour) else 9999
        prices[datetime.datetime(year, month, day, hour, 0)] = (Decimal(price), category)
    # ic(prices)
    return prices


def calculate_categories(date: datetime.date, prices: dict) -> dict:
    categories = [value[1] for key, value in prices.items()]
    counter = Counter(categories)
    # ic(counter)
    expensive_hours = counter.get(PriceCategories.EXPENSIVE)
    ic(expensive_hours)
    if expensive_hours and MINIMUM_HEATING_HOURS > 24 - expensive_hours:
        print(f'More heating hours are needed, {MINIMUM_HEATING_HOURS} > {24 - expensive_hours}')
        hours_tuple = [[date, price, category] for date, (price, category) in prices.items()]
        hours_sorted_by_price = sorted(hours_tuple, key=lambda x: x[1])
        for i in range(0, MINIMUM_HEATING_HOURS):
            date, price, category = hours_sorted_by_price[i]
            if category in (PriceCategories.EXPENSIVE, PriceCategories.NORMAL):
                hours_sorted_by_price[i][2] = PriceCategories.FORCED
        hours_sorted_by_time = sorted(hours_sorted_by_price, key=lambda x: x[0])
        # ic(hours_sorted_by_time, hours_sorted_by_price)
        prices = dict((date, (price, category)) for date, price, category in hours_sorted_by_time)
        # ic(prices)
    if len(prices) < 24:
        return fill_out_default_categories(date, prices)
    return prices