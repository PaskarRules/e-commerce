from django.http import JsonResponse, Http404
from django.core import serializers

from .models import *

import json


def ajax_get_order_info(request, pk):
    if not request.is_ajax():
        raise Http404

    order_items = list(OrderItem.objects.filter(order=pk))

    items = []
    for item in order_items:
        product_info = {
            'name': item.product.name,
            'image': item.product.imageURL,
            'qty': item.quantity,
            'price': item.product.price,
            'total': item.get_total,
            'url': item.product.get_product_url(),
        }
        items.append(product_info)

    items = json.dumps(items)

    return JsonResponse(items, safe=False)
