import datetime
from typing import Optional

import pytz
import logging
from icecream import ic
from nordpool import elspot
from filecache import filecache

# Initialize class for fetching Elspot prices
from energy_prices.models import Price

prices_spot = elspot.Prices()

hour_in_seconds = 60 * 60
area = 'FI'  # Clear the database before you change this


@filecache(8 * hour_in_seconds)
def get_hourly_prices(area) -> dict:
    logging.info(f'Fetching prices for {area} from Nordpool')
    result = prices_spot.hourly(areas=[area])
    ic(result)
    return result['areas'][area]['values']


# @filecache(8 * hour_in_seconds)
def update_hourly_prices() -> None:
    global area
    logging.info(f'Updating prices for {area}')
    prices = get_hourly_prices(area)
    for p in prices:
        price, created = Price.objects.update_or_create(
            start_time=p['start'], defaults=dict(price=p['value'])
        )
        print(f'Price {price.price} starting at {price.start_time}, created: {created}')



def get_current_price() -> Optional[float]:
    """
    # >>> type(get_current_price('FI'))
    <class 'float'>
    """
    global area
    prices = get_hourly_prices(area)
    current_price = [p for p in prices if
                     p['start'] < datetime.datetime.now(pytz.utc) < p['end']]
    return current_price[0]['value'] / 1000 if len(current_price) else None
