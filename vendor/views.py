from django.shortcuts import render, get_object_or_404
from vendor.forms import ProductForm
from vendor.forms import ShippingOptionsForm
from main.models import Product, Message, ShippingOptions
from orders.models import Order, OrderItem, Pay
from accounts.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView
from django.db.models import Q
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import redirect
from django.core.files.storage import FileSystemStorage
from datetime import date


# Create your views here.
# get current user
def get_user_id(request):
    current_user = request.user
    return current_user.id


# Add product
def add_product(request):
    form = ProductForm()
    owner_id = get_user_id(request)

    if request.user.is_vendor:
        return render(request, 'add_product.html', {'form': form, 'owner_id': owner_id})
    else:
        return HttpResponseRedirect('/')


# Delete poduct
def delete_product(request, product_id):
    product_delete = Product.objects.filter(id=product_id)
    product_delete.update(available=False)

    order_list = OrderItem.objects.filter(product_id=product_id).select_related('order')
    for order_item in order_list:
        if order_item.order.paid == "2":
            Order.objects.filter(id=order_item.order.id).update(paid=3)
            Pay.objects.filter(id=order_item.order.payment_id).update(status=3)

            user_id = order_item.order.user_id
            message_content = "Your shipping product are deleted by vendor so your shipping are cancelled. Please contact staff for refunding your payment."
            Message.objects.create(content=message_content, receiver=User.objects.get(id=user_id), sender=User.objects.get(username='admin'))

    msg = "Product are deleted. Shipping of deleted product are cancelled."
    messages.warning(request, msg)
    return list_products(request)


def update_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product_id = request.POST['productID']
            product = Product.objects.filter(id=product_id)[0]

            data = request.POST.copy()
            product_id = data.get('productID')
            name = data.get('name')
            slug = data.get('slug')
            description = data.get('description')
            price = data.get('price')
            available = data.get('available')
            if available == 'on':
                available = 1
            else:
                available = 0
            stock = data.get('stock')
            payout_address = data.get('payout_address')
            category = data.get('category')
            country = data.get('country')
            owner_id = data.get('productOwnerID')
            image = product.image

            if 'image' in request.FILES:
                fs = FileSystemStorage()
                uploaded_file = request.FILES['image']
                image = fs.save('products/{0}/{1}'.format(date.today().strftime("%Y/%m/%d"), uploaded_file.name),
                                uploaded_file)

            if 'image-clear' in request.POST:
                image = ''

            Product.objects.filter(id=product_id).update(name=name,
                                                         slug=slug,
                                                         description=description,
                                                         price=price,
                                                         available=available,
                                                         stock=stock,
                                                         payout_address=payout_address,
                                                         category=category,
                                                         country=country,
                                                         productOwnerID=owner_id,
                                                         image=image)

            msg = "Product are updated."
            messages.warning(request, msg)
            return list_products(request)


def shipping_options(request):
    form = None
    shipping_options = ShippingOptions.objects.all()
    shipping_options_count = ShippingOptions.objects.count()
    if shipping_options_count < 5:
        form = ShippingOptionsForm()
        context = {
            'shipping_options' : shipping_options,
            'form' : form
        }
    else:
        message = "You can only add 6 shipping options"
        messages.warning(request, message)
        context = {
        'shipping_options' : shipping_options,
        'new_message' : message
    }    
    if request.method == "POST":
        
        data = request.POST.dict()
        zone_name = data.get('zone_name')
        zone_type = data.get('zone_type')
        new = ShippingOptions.objects.create(zone_name = zone_name,zone_type= zone_type)
        shipping_options = ShippingOptions.objects.all()
        new.save()  # Now you
        if shipping_options_count > 7:
            return redirect('shipping_options')
    return render(request, 'shipping/shippingoptions.html', context)

def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    form = ProductForm(request.POST or None, instance=product)
    owner_id = get_user_id(request)
    return render(request, 'update_product.html', {'form': form, 'owner_id': owner_id, 'product_id': product_id})


# Save product
def save_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            print("Hello")
            product = form.save(commit=False)
            product.productOwnerID = request.user
            product.save()  # Now you can send it to DB
            return list_products(request)
        else:
            print(form.errors)
            raise Exception("405")
    else:
        raise Exception("405")


# Get list of products
def list_products(request):
    owner_id = get_user_id(request)
    products=Product.objects.filter(productOwnerID=owner_id, available=True)

    if request.user.is_vendor:
        return render(request, 'list_products.html', {'products': products})
    else:
        return HttpResponseRedirect('/')


def accept_order(request, order_id):
    order = Order.objects.filter(id=order_id)
    order.update(paid=7)
    pay = Pay.objects.filter(id=order.first().payment_id)
    pay.update(status=7)
    msg = "Order are accepted."
    messages.success(request, msg)
    return HttpResponseRedirect(reverse('vendor_list_new_order'))


def reject_order(request, order_id):
    order = Order.objects.filter(id=order_id)
    user_id = order.first().user_id
    order.update(paid=3)
    pay = Pay.objects.filter(id=order.first().payment_id)
    pay.update(status=3)

    message_content = "Sorry but your shopping cart are canceled by vendor. Please send BTC address to Site manager for refunding."
    new_message = Message.objects.create(content=message_content, receiver=User.objects.get(id=user_id), sender=User.objects.get(username='admin'))
    new_message.save()
    msg = "Order are cancelled."
    # messages.add_message(request, 5, messages.SUCCESS, msg)
    messages.warning(request, msg)

    # return HttpResponseRedirect(reverse('vendor_list_new_order'))
    return redirect('vendor_list_new_order')


class VendorNewOrderListView(LoginRequiredMixin, ListView):
    template_name = 'orders/order/new_order_list.html'
    context_object_name = "orders"

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_vendor:
            return HttpResponseRedirect('/')

    def get_queryset(self):
        return Order.objects.filter(paid=2, user=self.request.user).select_related('payment')


class VendorNewOrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'orders/order/new_order_detail.html'
    context_object_name = "order_detail"

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_vendor:
            return HttpResponseRedirect('/')

    def get_object(self, queryset=None):
        order_id = self.kwargs.get("order_id")
        orders = OrderItem.objects.filter(order_id=order_id, author=self.request.user)
        return orders


class VendorShippedOrderListView(LoginRequiredMixin, ListView):
    template_name = 'orders/order/ship_order_list.html'
    context_object_name = "orders"

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_vendor:
            return HttpResponseRedirect('/')

    def get_queryset(self):
        return Order.objects.filter(paid=7).select_related('payment')


class VendorShippedOrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'orders/order/ship_order_detail.html'
    context_object_name = "order_detail"

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_vendor:
            return HttpResponseRedirect('/')

    def get_object(self, queryset=None):
        order_id = self.kwargs.get("order_id")
        orders = OrderItem.objects.filter(order_id=order_id, author=self.request.user)
        return orders


class VendorCompleteOrderListView(LoginRequiredMixin, ListView):
    template_name = 'orders/order/complete_order_list.html'
    context_object_name = "orders"

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_vendor:
            return HttpResponseRedirect('/')

    def get_queryset(self):
        return Order.objects.filter(paid=8).select_related('payment')


class VendorCompleteOrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'orders/order/complete_order_detail.html'
    context_object_name = "order_detail"

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_vendor:
            return HttpResponseRedirect('/')

    def get_object(self, queryset=None):
        order_id = self.kwargs.get("order_id")
        orders = OrderItem.objects.filter(order_id=order_id, author=self.request.user)
        return orders


class VendorCancelOrderListView(LoginRequiredMixin, ListView):
    template_name = 'orders/order/cancel_order_list.html'
    context_object_name = "orders"

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_vendor:
            return HttpResponseRedirect('/')

    def get_queryset(self):
        return Order.objects.filter(Q(paid=3) | Q(paid=4)).select_related('payment')


class VendorCancelOrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'orders/order/cancel_order_detail.html'
    context_object_name = "order_detail"

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_vendor:
            return HttpResponseRedirect('/')

    def get_object(self, queryset=None):
        order_id = self.kwargs.get("order_id")
        orders = OrderItem.objects.filter(order_id=order_id, author=self.request.user)
        return orders


class VendorDisputeOrderListView(LoginRequiredMixin, ListView):
    template_name = 'orders/order/dispute_order_list.html'
    context_object_name = "orders"

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_vendor:
            return HttpResponseRedirect('/')

    def get_queryset(self):
        return Order.objects.filter(Q(paid=5) | Q(paid=6)).select_related('payment')


class VendorDisputeOrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'orders/order/new_order_detail.html'
    context_object_name = "order_detail"

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_vendor:
            return HttpResponseRedirect('/')

    def get_object(self, queryset=None):
        order_id = self.kwargs.get("order_id")
        orders = OrderItem.objects.filter(order_id=order_id, author=self.request.user)
        return orders.first()


