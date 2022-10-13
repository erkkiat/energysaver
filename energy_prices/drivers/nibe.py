import os

from energy_prices.categories import PriceCategories
from energy_prices.drivers.base import Device
import RPi.GPIO as GPIO
from grove.factory import Factory

from energy_prices.message import message

USE_GROVE = bool(os.environ.get('USE_GROVE', False))


class NibeF1226(Device):
    vendor = 'Nibe'
    model = 'F1226'
    port_number = None
    relay1 = None

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
        # super().set_price_category(category)
        cheap_electricity = bool(category in (PriceCategories.EXTREMELY_CHEAP, PriceCategories.CHEAP))
        message(f'Setting Rasberry Pi relay to {cheap_electricity}')
        if USE_GROVE:
            self.relay1.on() if cheap_electricity else self.relay1.off()
        else:
            GPIO.output(self.port_number, cheap_electricity)
