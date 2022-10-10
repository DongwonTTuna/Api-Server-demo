import json
from django.http.response import JsonResponse
from .dbfunc import *
# Create your views here.




def chart(request):
    if request.method != 'GET':
        return JsonResponse({})
    exchange = request.Get.get(key="exchange", default="BINANCE")
    symbol = request.Get.get(key="symbol", default="BTCUSDT")
    return JsonResponse(fetch_chartdata(exchange,symbol))


def exchanges(request):
    if request.method != 'GET':
        return JsonResponse({})
    return JsonResponse(fetch_exchanges())

## Parameters = exchange = "EXCHANGE"
def ticker(request):
    if request.method != 'GET':
        return JsonResponse({})
    exchange = request.GET.get(key="exchange", default="BINANCE")
    return JsonResponse(fetch_tickers(exchange))