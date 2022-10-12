from energy_prices.categories import PriceCategories
from energy_prices.drivers.base import Device
import RPi.GPIO as GPIO


class NibeF1226(Device):
    vendor = 'Nibe'
    model = 'F1226'
    output_number = None

    def __init__(self, output_number: int):
        self.output_number = output_number
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(output_number, GPIO.OUT)
        super().__init__(output_number)

    def set_price_category(self, category: PriceCategories) -> bool:
        """
        The pins we are connecting to on the Nibe F1226 need to be set to "external control" or "ulkoinen säätö"
        """
        # super().set_price_category(category)
        cheap_electricity = bool(category in (PriceCategories.EXTREMELY_CHEAP, PriceCategories.CHEAP))
        print(f'Setting Rasberry Pi output {self.output_number} to {cheap_electricity}')
        return GPIO.output(self.output_number, cheap_electricity)
