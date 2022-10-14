import os

from energy_prices.categories import PriceCategories
from energy_prices.drivers.base import Device
import RPi.GPIO as GPIO

from energy_prices.message import messages

USE_GROVE = bool(os.environ.get('USE_GROVE', False))
if USE_GROVE:
    from grove.factory import Factory

AUX_MODE = os.environ.get('AUX_MODE', 'increased heating')  # A name for the function you have configured on Nibe


class NibeF1226(Device):
    vendor = 'Nibe'
    model = 'F1226'
    port_number = None
    relay1 = None  # Only used for Grove

    def __init__(self, port_number: int):
        self.port_number = port_number
        if USE_GROVE:
            self.relay1 = Factory.getGpioWrapper("Relay", port_number)
        else:
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(port_number, GPIO.OUT)
        super().__init__(port_number)

    def set_price_category(self, category: PriceCategories):
        """
        The pins we are connecting to on the Nibe F1226 need to be set to "external control" or "ulkoinen säätö"
        """
        cheap_electricity = bool(category in (PriceCategories.EXTREMELY_CHEAP, PriceCategories.CHEAP))
        messages.message(f'Setting {AUX_MODE} to {cheap_electricity}')
        if USE_GROVE:
            self.relay1.on() if cheap_electricity else self.relay1.off()
        else:
            GPIO.output(self.port_number, cheap_electricity)
