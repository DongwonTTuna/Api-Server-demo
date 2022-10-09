import json
from django.http.response import JsonResponse
# Create your views here.


def api(request):
    if request.method != 'GET':
        return JsonResponse({})
    exchange = request.Get.get(symbol="exchange", default="BINANCE")
    ticker = request.Get.get(symbol="exchange", default="BINANCE")
    exchange = request.Get.get(symbol="exchange", default="BINANCE")
    exchange = request.Get.get(symbol="exchange", default="BINANCE")
    ret = {}
    return JsonResponse(ret)