from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http.response import HttpResponse
from django.shortcuts import render, redirect

from django.http import JsonResponse

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.db.models import Q
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

import json
import datetime


from liqpay.liqpay import LiqPay

from .models import *
from .forms import CustomerForm
from .utils import cartData, guestOrder

from django.conf import settings

from .filters import filter_pr

from liqpay import liqpay as lqp


class PayView(TemplateView):
    template_name = 'store/billing.html'
    @csrf_exempt
    def get(self, request, *args, **kwargs):
        order = Order.objects.get(pk=kwargs['pk'])
        liqpay = lqp.LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
        params = {
            'action': 'pay',
            'amount': str(order.get_cart_total),
            'currency': 'UAH',
            'description': 'Payment for cosmetics',
            'order_id': str(order.id),
            'version': '3',
            'sandbox': 1,  # sandbox mode, set to 1 to enable it
            'server_url': 'http://127.0.0.1:8000/pay-callback/',
            'result_url': 'http://127.0.0.1:8000/pay-callback/',  # url to callback view
        }
        signature = liqpay.cnb_signature(params)
        data = liqpay.cnb_form(params)
        f = data.rfind('value="')
        s = data.rfind('"/>')
        signature = data[f + 7:s]
        first = data.find('value="')
        second = data.find('"/>')
        data = data[first + 7:second]

        return render(request, self.template_name, {'signature': signature, 'data': data})

# @csrf_exempt
# def callback(request):
#     # print(request.POST.get('data'))
#     data = json.loads(request.body)
#     print(data)
#     return JsonResponse('Payment submitted...')


@method_decorator(csrf_exempt, name='dispatch')
class PayCallbackView(View):
    def post(self, request, *args, **kwargs):
        liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
        data = request.POST.get('data')
        signature = request.POST.get('signature')
        sign = liqpay.str_to_sign(settings.LIQPAY_PRIVATE_KEY + data + settings.LIQPAY_PRIVATE_KEY)
        if sign == signature:
            print('callback is valid')
        response = liqpay.decode_data_from_str(data)
        print(response)
        # if 'err_code' in response:
        #     pass
        # else:
        if response:
            order = Order.objects.get(id=response['order_id'])
            print('ORDER', order)
            order.status = 'Payed'
            order.date_ordered = datetime.datetime.now()
            order.total_price = response['amount']
            order.save()
        print('callback data', response)
        return redirect('store')


def megamenu():
    cats = Category.objects.all()

    cats_childs = []
    cats_parents = []
    for cat in cats:
        if cat.name == 'default':
            continue
        if cat.parent:
            cats_parents.append(cat.parent)
        if not cat.parent and cat.parent not in cats_parents:
            cats_parents.append(cat)

    cats_parents = set(cats_parents)

    for cat in cats:
        if cat in cats_parents:
            continue
        else:
            cats_childs.append(cat)

    return cats_parents, cats_childs


@login_required(login_url='login')
def userPage(request):
    data = cartData(request)

    cartItems = data['cartItems']
    items = data['items']

    if request.GET.get('status'):
        featured_filter = request.GET.get('status')
        orders_list = request.user.customer.order_set.filter(status=featured_filter)
    else:
        orders_list = request.user.customer.order_set.filter(~Q(status='Cart_order'))

    page = request.GET.get('page', 1)

    paginator = Paginator(orders_list, 5)
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

    customer = Customer.objects.get(user=request.user.customer.user)
    total_orders = orders_list.count()

    cats_parents, cats_childs = megamenu()

    statuses = Order.STATUS
    statuses = statuses[1:]
    context = {
        'items': items, 'orders': orders, 'cartItems': cartItems, 'customer': customer,
        'total_orders': total_orders, 'parents': cats_parents, 'childs': cats_childs, 'statuses': statuses}
    return render(request, 'store/user.html', context)


@login_required(login_url='login')
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)
    form_pass = PasswordChangeForm(user=request.user)

    if request.method == 'POST' and request.POST.get('chng-data') == 'data':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('user-page')

    if request.method == 'POST' and request.POST.get('chng-pass') == 'pass':
        form_pass = PasswordChangeForm(user=request.user, data=request.POST)
        if form_pass.is_valid():
            form_pass.save()
            update_session_auth_hash(request, form_pass.user)

            send_mail(
                'New Account!', 'Password was changed!',
                settings.EMAIL_HOST_USER, [request.user.email], fail_silently=False
            )
            messages.success(request, 'Password was cahnged for ' + request.user.username)

            return redirect('user-page')

    data = cartData(request)

    cartItems = data['cartItems']

    cats_parents, cats_childs = megamenu()

    context = {'form': form, 'form_pass': form_pass, 'cartItems': cartItems, 'parents': cats_parents,
               'childs': cats_childs}
    return render(request, 'store/customer_settings.html', context)

@csrf_exempt
def store(request):
    data = cartData(request)

    cartItems = data['cartItems']
    products = Product.objects.all()

    cats_parents, cats_childs = megamenu()

    if request.GET.get('products'):
        products_filter = request.GET.get('products')
        products = Product.objects.order_by(products_filter).all()
        # filter_pr(products_filter)

    context = {'products': products, 'cartItems': cartItems, 'parents': cats_parents, 'childs': cats_childs}
    return render(request, 'store/store.html', context)


def product(request, pk):
    data = cartData(request)

    cartItems = data['cartItems']
    cur_product = Product.objects.get(pk=pk)

    cats_parents, cats_childs = megamenu()

    context = {'product': cur_product, 'cartItems': cartItems, 'parents': cats_parents, 'childs': cats_childs}
    return render(request, 'store/product.html', context)


def categories(request, slug):
    data = cartData(request)

    cartItems = data['cartItems']
    category = Category.objects.get(slug=slug)
    products = Product.objects.filter(category=category.id)
    cats_parents, cats_childs = megamenu()

    context = {'products': products, 'cartItems': cartItems, 'category': category, 'parents': cats_parents,
               'childs': cats_childs}
    return render(request, 'store/store.html', context)


def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    cats_parents, cats_childs = megamenu()

    context = {'items': items, 'order': order, 'cartItems': cartItems, 'parents': cats_parents, 'childs': cats_childs}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    cats_parents, cats_childs = megamenu()

    context = {'items': items, 'order': order, 'cartItems': cartItems, 'parents': cats_parents, 'childs': cats_childs}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, status='Cart_order')

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    elif action == 'cancel':
        orderItem.quantity = 0
    elif action == 'set':
        orderItem.quantity = int(data['value'])

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def cancelOrder(request):
    data = json.loads(request.body)
    orderId = data['orderId']
    action = data['action']

    customer = request.user.customer
    order = Order.objects.get(id=orderId)

    if action == 'cancel':
        order.status = 'Canceled'

    order.save()

    return JsonResponse('Замовлення скасовано!', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, status='Cart_order')
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])

    order.transaction_id = transaction_id
    order.date_ordered = datetime.datetime.now()

    if total == order.get_cart_total:
        order.total_price = total
        order.status = 'Not confirmed'
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse(order.id, safe=False)
