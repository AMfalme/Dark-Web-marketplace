from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from main.models import Product
from .cart import Cart
from .forms import CartAddProductForm
from main.models import Category
from cryptowatch_client import Client
from main.models import Message


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
    crypto_price = {"btcusd": btcusd_price, 'btcgbp': btcgbp_price, 'btceur': btceur_price}
    return crypto_price


@require_POST
def cart_add(request, product_id):
    if request.user.is_admin == False:
        return redirect("/")
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product, quantity=cd['quantity'], update_quantity=cd['update'])
    # return redirect('cart:cart_detail')
    return redirect('orders:order_create', product_id=product_id)


def cart_remove(request, product_id):
    if request.user.is_admin == False:
        return redirect("/")
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


def cart_detail(request):
    if request.user.is_authenticated == False:
        return redirect("signin")

    if request.user.is_admin == False:
        return redirect("/")

    cart = Cart(request)
    categories = Category.objects.all()
    crypto_data = crypto_currencies()
    message = len(Message.objects.filter(check=False))
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={'quantity': item['quantity'], 'update': True})
    context = {
        'cart': cart,
        'categories': categories,
        'crypto_data': crypto_data,
        'new_message': message
    }
    return render(request, 'cart/detail.html', context)
