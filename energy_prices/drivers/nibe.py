import os
from enum import Enum

from energy_prices.categories import PriceCategories
from energy_prices.drivers.base import Device
import RPi.GPIO as GPIO

from energy_prices.message import messages

USE_GROVE = bool(os.environ.get('USE_GROVE', False))
if USE_GROVE:
    from grove.factory import Factory


class AuxModes(Enum):
    TARIFF_BLOCKING = 'TA', 'The additional heat, the compressor, the heating and hot water are blocked'
    TEMPORARY_LUX = 'LU', 'The water heater is set to the high temperature setting'
    EXTERNAL_ADJUSTMENT = 'EX', 'Increase the supply temperature and the room temperature'


AUX_MODE = os.environ.get('AUX_MODE')
options = [x.name for x in AuxModes]
if AUX_MODE not in options:
    msg = f'Please set the AUX_MODE to one of {", ".join(options)} for the Nibe F1226'
    messages.message(msg)
    raise ValueError(msg)


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
        output = bool(category in dict(
            EXTERNAL_ADJUSTMENT=(PriceCategories.EXTREMELY_CHEAP, PriceCategories.CHEAP, PriceCategories.FORCED),
            TEMPORARY_LUX=(PriceCategories.EXTREMELY_CHEAP, PriceCategories.CHEAP, PriceCategories.FORCED),
            TARIFF_BLOCKING=(PriceCategories.EXPENSIVE,),
        )[AUX_MODE])

        messages.message(f'Setting {AUX_MODE} to {"ON" if output else "off"}')
        if USE_GROVE:
            self.relay1.on() if extra_heating else self.relay1.off()
        else:
            GPIO.output(self.port_number, extra_heating)
