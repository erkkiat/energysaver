from django.utils.module_loading import import_string

from django.conf import settings
from django.http import HttpResponse

from energy_prices.drivers.base import Device
from energy_prices.fetch_vattenfall import get_current_price

Driver = import_string(settings.DRIVER)
driver: Device = Driver(settings.HARDWARE_PORT_NUMBER)


def fetch_prices(request):
    category, price = get_current_price()
    print(f'Success of setting the price category for {driver.vendor} {driver.model}: '
          f'{driver.set_price_category(category)}')
    return HttpResponse(f'The price category right now: {category}, price: {price:.2f} €/kWh')
