from collections import Counter
from decimal import Decimal
from enum import Enum
from typing import Union

from icecream import ic

THRESHOLD_EXTREMELY_CHEAP = 0.02
THRESHOLD_CHEAP = 0.06
THRESHOLD_EXPENSIVE = 0.14


class PriceCategories(Enum):
    EXTREMELY_CHEAP = 1
    CHEAP = 2
    NORMAL = 3
    EXPENSIVE = 4

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
    # ic(categories, counter)
    return counter