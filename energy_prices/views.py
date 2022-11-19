from django.utils.module_loading import import_string

from django.conf import settings
from django.http import HttpResponse

from energy_prices.categories import PriceCategories
from energy_prices.drivers.base import Device
from energy_prices.fetch_vattenfall import get_current_price

from energy_prices.message import messages

Driver = import_string(settings.DRIVER)
driver: Device = Driver(settings.HARDWARE_PORT_NUMBER)


def fetch_prices(_request):
    done = False
    try:
        category, price = get_current_price()
        msg = f'{price:.2f} €/kWh, {category.name}'
        messages.message(msg)
        driver.set_price_category(category)
        done = True
        messages.flush()
        return HttpResponse('')
    except Exception as e:
        messages.message(f'Error fetching prices or adjusting heating: {e}', immediate=True)
        if not done:
            messages.message('**** Adjustments have not been made, reverting to no tariff blocking.')
            driver.set_price_category(PriceCategories.CHEAP)
        return HttpResponse(f'Error fetching prices or adjusting heating: {e}')
