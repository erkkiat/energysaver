from collections import Counter
from decimal import Decimal
from enum import Enum
from typing import Union

from icecream import ic

THRESHOLD_EXTREMELY_CHEAP = 0.02
THRESHOLD_CHEAP = 0.06
THRESHOLD_EXPENSIVE = 0.14
MINIMUM_HEATING_HOURS = 8


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


def calculate_categories(prices: dict) -> Counter:
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
            if category == PriceCategories.EXPENSIVE:
                hours_sorted_by_price[i][2] = PriceCategories.FORCED
        hours_sorted_by_time = sorted(hours_sorted_by_price, key=lambda x: x[0])
        # ic(hours_sorted_by_time, hours_sorted_by_price)
        prices = dict((date, (price, category)) for date, price, category in hours_sorted_by_time)
        # ic(prices)
    return prices