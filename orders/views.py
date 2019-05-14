from django.shortcuts import render,redirect, get_object_or_404
from .models import OrderItem,Order,Pay
from .forms import OrderCreateForm
from cart.cart import Cart
from accounts.forms import SignUpForm
from django.contrib.auth import login, authenticate
import requests
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from main.models import Category, Product
from cryptowatch_client import Client

"""
rememeber to add cart.clear()
"""


def crypto_currencies():
    client = Client(timeout=30)
    btcgbp = client.get_markets_price(exchange='gdax', pair='btcgbp')
    btcusd = client.get_markets_price(exchange='gdax', pair='btcusd')
    btceur = client.get_markets_price(exchange='gdax', pair='btceur')
    btcgbp_response = btcgbp.json()
    btcusd_response = btcusd.json()
    btceur_response = btceur.json()
    btcgbp_price = btcgbp_response.get('result').get('price')
    btcusd_price = btcusd_response.get('result').get('price')
    btceur_price = btceur_response.get('result').get('price')
    crypto_price = {'btcusd': btcusd_price, 'btcgbp': btcgbp_price, 'btceur': btceur_price}
    return crypto_price


def waiting(request,order_id, address, cost):
    content = "Will send you message after confirm your transaction. Please wait some times during confirm your transaction."
    return render(request, "orders/order/waiting.html", {'content': content})


def pay(request, order_id, product_id):
    cart = Cart(request)
    btc_course = (requests.get("https://api.coindesk.com/v1/bpi/currentprice/USD.json").json())["bpi"]['USD']["rate_float"]
    total_price = cart.get_total_price(product_id)
    btc_price = round((float(cart.get_total_price(product_id))/float(btc_course)), 8)
    if total_price > 0:
        rpc_user = "NSA12012"
        rpc_password = "ZIwnhqsa"
        rpc_connection = AuthServiceProxy("http://%s:%s@213.227.140.1:8332" % (rpc_user, rpc_password))
        print("=============================")
        address = rpc_connection.getnewaddress()
        print(address)
        pay = Pay.objects.create(timestamp=timezone.now(), btc_course=btc_course, amount_expected=btc_price,
                                 amount_received=0, author=request.user.username, status=0, address=address)
        pay.save()
        Order.objects.filter(id=order_id).update(payment=pay, paid="1")
        cart.clear_item(product_id)
        return render(request, 'orders/order/pay.html',
                      {'order_id': order_id,
                       'address': address,
                       'btc_course': btc_course,
                       'total_price': total_price,
                       'btc_price': btc_price})

    else:
        content = "Cart Items are Zero. Please cart products."
        return render(request, "orders/order/waiting.html", {'content': content})


def order_create(request, product_id):
    cart = Cart(request)
    categories = Category.objects.all()
    product = get_object_or_404(Product, id=product_id)
    crypto_data = crypto_currencies()
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = OrderCreateForm(request.POST)
            if form.is_valid():
                print("addrr===>> ", form['address'].value())
                order = Order.objects.create(
                    user=request.user,
                    address=form['address'].value()
                )
                print("----->>> ", order)

                OrderItem.objects.create(
                    author=request.user,
                    order=order,
                    product=product,
                    price=cart.get_item_price(product_id),
                    quantity=cart.get_item_quantity(product_id)
                )

                product = Product.objects.get(id=product_id)
                stock = product.stock - cart.get_item_quantity(product_id)
                Product.objects.filter(id=product_id).update(stock=stock)
                return HttpResponseRedirect(reverse('orders:pay', kwargs={'order_id': order.id, 'product_id': product_id}))
        else:
            form = OrderCreateForm()
        context = {
            'form': form,
            'categories': categories,
            'crypto_data': crypto_data,
            'product_id': int(product_id)
        }
        return render(request, 'orders/order/create.html', context)
    elif not request.user.is_authenticated:
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                login(request, user)
                return redirect('orders:order_create')
            else:
                form = SignUpForm()
                return render(request, 'orders/order/create.html', {'form': form})
        else:
            form = SignUpForm()
            return render(request, 'orders/order/create.html', {'form': form})
