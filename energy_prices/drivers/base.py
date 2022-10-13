from energy_prices.categories import PriceCategories


class Device:
    vendor = 'Simulator'
    model = 'Hal'

    def __init__(self, port_number: int):
        print(f'Setting port number to {port_number}')

    def set_price_category(self, category: PriceCategories) -> bool:
        print(f'Simulating the setting of price category {category}.')
        print('To trigger real actions, set settings.DRIVER to a class inherited from Device.\n')
        if category == PriceCategories.EXPENSIVE:
            print('EXPENSIVE electricity, simulating a failed set_price_category()')
            return False
        return True
