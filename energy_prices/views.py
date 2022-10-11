from django.http import HttpResponse
from django.shortcuts import render

from energy_prices.fetch_vattenfall import update_hourly_prices, get_current_price


def fetch_prices(request):
    update_hourly_prices()
    return HttpResponse(str(get_current_price()))
