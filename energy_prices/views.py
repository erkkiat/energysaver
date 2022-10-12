from django.utils.module_loading import import_string

from django.conf import settings
from django.http import HttpResponse

from energy_prices.categories import PriceCategories
from energy_prices.drivers.base import Device
from energy_prices.fetch_vattenfall import get_current_price

from energy_prices.message import message

Driver = import_string(settings.DRIVER)
driver: Device = Driver(settings.HARDWARE_PORT_NUMBER)


def fetch_prices(_request):
    category, price = get_current_price()
    msg = f'Price: {price:.2f} €/kWh, rating: {category.name}'
    message(msg)
    driver.set_price_category(category)
    return HttpResponse('')
