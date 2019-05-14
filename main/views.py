from cart.forms import CartAddProductForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404, redirect

from .models import Category, Product, Message
from django_countries import countries
from accounts.models import User, VendorTerm
from accounts.forms import LoginForm
from django.db.models import Q
from django.db.models import Avg, Sum

from django.template.defaulttags import register
from background.views import crypto_currencies


@register.filter
def get(dictionary, key):
    return dictionary.get(key)


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    message = len(Message.objects.filter(check=False))
    #message = len(Message.objects.all())
    form = LoginForm
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category)

    #cryptocurrenies Data
    crypto_data = crypto_currencies()

    ratings = {}
    sold_cnt = {}
    for product in products:
        rating_total = 0
        rating_count = 0
        for order_item in product.order_items.filter(order__paid='8'):
            for rating in order_item.ratings.all():
                rating_total += rating.total * order_item.quantity
                rating_count += rating.count * order_item.quantity
        ratings[product.id] = 0 if rating_count == 0 else rating_total/rating_count
        sold_cnt[product.id] = product.order_items.filter(order__paid='8').aggregate(Sum('quantity'))['quantity__sum']
        sold_cnt[product.id] = 0 if sold_cnt[product.id] is None else sold_cnt[product.id]

    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'ratings': ratings,
        'sold_cnt': sold_cnt,
        # 'crypto_data': crypto_data,
        'countries': countries,
        'form': form,
        'new_message': message,
    }

    return render(request, 'main/product/list.html', context)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    cart_product_form = CartAddProductForm()
    product_stock = cart_product_form.get_product_stock(id)
    categories = Category.objects.all()
    crypto_data = crypto_currencies()
    message = len(Message.objects.filter(check=False))

    product_vendor = Product.objects.values('productOwnerID', 'country').get(id=id)
    country = countries.name(product_vendor.get('country'))
    product_vendor = product_vendor.get('productOwnerID')

    vendor = User.objects.values('id', 'username').filter(id=product_vendor, vendor=True)
    term_conditions = VendorTerm.objects.filter(userId=product_vendor)

    rating_total = 0
    rating_count = 0
    for order_item in product.order_items.filter(order__paid='8'):
        for rating in order_item.ratings.all():
            rating_total += rating.total * order_item.quantity
            rating_count += rating.count * order_item.quantity

    context = {
        'product': product,
        'categories': categories,
        'cart_product_form': cart_product_form,
        'product_stock': product_stock,
        'vendor': vendor[0],
        'avg_rating': 0 if rating_count == 0 else rating_total/rating_count,
        'country': country,
        'crypto_data': crypto_data,
        'new_message': message,
        'term_conditions': term_conditions[0]
    }
    return render(request, 'main/product/detail.html', context)


def search(request):
    if request.method == 'GET':
        message = len(Message.objects.filter(check=False))
        price = 0
        if request.GET.get('price'):
            price = int(request.GET.get('price'))

        country = request.GET.get('country', None)
        category = request.GET.get('category', None)
        category_id = Category.objects.filter(name=category)
        products = {}

        if price > 0 and category is '' and country is '':
            products = Product.objects.filter(Q(price__gte=price))
        elif category and price is 0 and country is '':
            print("===================================")
            products = Product.objects.filter(category__in=category_id)
        elif country and price is 0 and category is '':
            products = Product.objects.filter(country=country)
        elif price > 0 and category and country is '':
            products = Product.objects.filter(Q(price__gte=price), category__in=category_id)
        elif country and price > 0 and category is '':
            products = Product.objects.filter(Q(price__gte=price), country=country)
        elif country and category and price is 0:
            products = Product.objects.filter(country=country, category__in=category_id)
        elif price > 0 and category and country:
            products = Product.objects.filter(Q(price__gte=price), category__in=category_id, country=country)
        elif price is 0 and category is '' and country is '':
            products = Product.objects.all

        categories = Category.objects.all()
        # cryptocurrenies Data
        crypto_data = crypto_currencies()

        context = {
            'category': category,
            'categories': categories,
            'products': products,
            'crypto_data': crypto_data,
            'countries': countries,
            'new_message': message

        }
    else:
        raise Exception("405")
    return render(request, 'main/product/list.html', context)


# User Notification page
class UserMessageListView(LoginRequiredMixin, ListView):
    template_name = 'message/message_list.html'
    context_object_name = "messages"

    def get_queryset(self):
        admin_ids = User.objects.filter(admin=True)
        return Message.objects.filter(Q(sender__in=admin_ids) & Q(receiver=self.request.user)).order_by('-create')


# User Inbox page
class UserInboxListView(LoginRequiredMixin, ListView):
    template_name = 'inbox/inbox_list.html'
    context_object_name = "messages"

    def get_queryset(self):
        return Message.objects.filter((Q(sender=self.request.user) & Q(sender_removed=False)) |
                                      (Q(receiver=self.request.user) & Q(receiver_removed=False))).order_by('-create')
               #| Message.objects.filter(sender=self.request.user)


# User Inbox Send page
def inbox_send(request, receiver_id = '0'):
    if request.method == 'POST':
        obj = Message()
        obj.sender_id = request.user.id
        obj.receiver_id = request.POST.get('receiver_id')
        obj.content = request.POST.get('content')
        obj.save()

        msg = "Message sent successfully"
        messages.success(request, msg)
        return redirect("inbox_send")
    else:
        users = User.objects.all
        context_object = {'users': users, 'receiver_id': int(receiver_id)}
    return render(request, 'inbox/inbox_send.html', context_object)


# User Inbox Delete Message
def delete_message(request, message_id=''):
    message = Message.objects.get(pk=message_id)
    message_object = Message.objects.filter(id=message_id)

    if message.sender_id == request.user.id:
        message_object.update(sender_removed=True)
    elif message.receiver_id == request.user.id:
        message_object.update(receiver_removed=True)

    msg = "Message is deleted"
    messages.success(request, msg)
    return redirect("inbox_list")

