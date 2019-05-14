import gnupg
from pprint import pprint

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, FormView
from orders.models import OrderItem, Order, User, Pay
from django.shortcuts import render, get_object_or_404, redirect

from .forms import SignUpForm, LoginForm, UserPgpChangeForm, Changetermsform
from dark_web.mixins import RequestFormAttachMixin
from accounts.models import User as VendorUser
from accounts.models import VendorTerm, VendorFavorite
from main.models import Product, Message
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone
import requests
from bitcoinrpc.authproxy import AuthServiceProxy
from django.db.models import Sum

from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from background.views import crypto_currencies
# Create your views here.


# User ORDER details page
class UserOrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'orders/order_detail.html'
    context_object_name = "order"

    def get_object(self, queryset=None):
        order_id = self.kwargs.get("order_id")
        if Order.objects.filter(id=order_id).count() > 0:
            return Order.objects.filter(id=order_id)[0]
        else:
            return None
        # order_item = OrderItem.objects.filter(
        #     order_id=order_id, author=self.request.user)

        # order = Order.objects.filter(id=order_id).first()
        # return order

        # return order_item


# User ORDER(s) page
class UserOrdersListView(LoginRequiredMixin, ListView):
    template_name = 'orders/order_list.html'
    context_object_name = "orders"

    def get_queryset(self):
        Order.objects.filter(~Q())
        time_delta = timezone.now() - timedelta(hours=2)
        # return Order.objects.filter(payment_id__isnull=False , user=self.request.user)
        # aaa = Order.objects.filter(updated__range=(time_delta, timezone.now()))
        return Order.objects.filter(Q(updated__range=(time_delta, timezone.now()), paid=1, user=self.request.user) | Q(user=self.request.user, paid__gt=1)).select_related('payment')

# User PROFILE update page


class UserPgpUpdateView(LoginRequiredMixin, FormView):
    form_class = UserPgpChangeForm
    template_name = "profile/update_pgp.html"

    def get_context_data(self, **kwargs):
        context = super(UserPgpUpdateView, self).get_context_data(**kwargs)
        context['pgp_form'] = UserPgpChangeForm
        return context

    # def get_object(self, queryset=None):
    #     return self.request.user

    def form_valid(self, form):
        print("Valid")
        request = self.request
        user = self.request.user
        print(request.user)
        print(form.cleaned_data)
        pgp_key = form.cleaned_data.get('pgp_key')
        user.pgp_key = pgp_key
        user.save()
        print("Confirm")
        print(user.pgp_key)
        msg = "PGP Key updated successfully"
        messages.success(request, msg)
        return redirect("user_profile")

    def form_invalid(self, form):
        print("Invalid")
        request = self.request
        msg = "Form invalid"
        messages.success(request, msg)
        return redirect("user_profile")


# User PROFILE update page
class Changeterms(LoginRequiredMixin, FormView):
    form_class = Changetermsform
    template_name = "profile/change_terms.html"

    def get_context_data(self, **kwargs):
        context = super(Changeterms, self).get_context_data(**kwargs)
        context['terms_form'] = Changetermsform
        return context

    # def get_object(self, queryset=None):
    #     return self.request.user

    def form_valid(self, form):
        print("Valid")
        print("this is the form", form.cleaned_data)
        user = self.request.user
        print("this is the user", user)
        desc = form.cleaned_data.get('description')
        new_term = VendorTerm(userId=user, description=desc)
        new_term.save()
        return redirect("user_profile")

    def form_invalid(self, form):
        print("Invalid")
        request = self.request
        msg = "Form invalid"
        messages.success(request, msg)
        return redirect("user_profile")


# User PROFILE page
class UserProfileView(LoginRequiredMixin, DetailView):
    template_name = "profile/user_profile.html"
    model = User

    def get_context_data(self, **kwargs):
        context = {}
        try:
            terms = VendorTerm.objects.get(userId=self.request.user)
            print(terms)
            context['terms'] = VendorTerm.objects.get(userId=self.request.user).description
        except:
            context['terms'] = None
        return context
    #    #context = super(UserProfileView, self).get_context_data(**kwargs)
    #    message = len(Message.objects.filter(check=False))
    #    #context['pgp_form'] = UserPgpChangeForm
    #    #context['new_message'] = message
    #    context = {
    #        'user': self.request.user,
    #        'new_message': message
    #    }

    def get_object(self, queryset=None):
        return self.request.user


# User Sign-up View
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            raw_password = form.cleaned_data.get('password1')
            user_ = form.save()
            user = authenticate(username=user_.username, password=raw_password)
            login(request, user)

            code_bip39 = user.code_bip39
            msg = "Hello " + user.username.upper() + ". Welcome to Euromarket.<p>    \
                    THIS IS YOUR RECOVERY SEED. WRITE IT DOWN. IN THE CASE YOU LOST ACCESS YOU CAN ONLY RECOVERY YOUR ACCOUNT IF YOU CAN PROVIDE US THE CORRECT WORDCOMBINATION."
                    #Code: " + code_bip39.upper()

            messages.success(request, mark_safe(msg))
            return redirect("product_list")
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


# GPG auth
def gpg_auth(request):
    # decrypt randomstring with users
    user = User.objects.get(username = request.session['username'])
    gpg = gnupg.GPG()
    import_result = gpg.import_keys(user.pgp_key)
    pprint(import_result.results)

    encrypted_data = gpg.encrypt(request.session['org_key'],
                                 import_result.fingerprints[0],
                                 armor=True,
                                 always_trust=True)

    encrypted_string = str(encrypted_data)
    print(str(encrypted_data.ok))
    print(encrypted_string)
    return render(request, "gpg_auth.html", {"enc_message": encrypted_string})


def gpg_verify(request):
    error_url = '/signin/gpg_auth/'
    success_url = '/'

    if request.method == 'POST':

        message = request.POST['message']

        if message != request.session['org_key']:
            msg = "Invalid Key"
            messages.error(request, msg)
            return redirect(error_url)

        username = request.session['username']
        password = request.session['password']
        user = authenticate(request, username=username, password=password)
        login(request, user)
        msg = "Welcome back " + user.username.upper()
        messages.success(request, msg)
        return redirect(success_url)

    msg = "Error Invalid Key"
    messages.error(request, msg)
    return redirect(error_url)


# User Sign-in View
class LoginView(RequestFormAttachMixin, FormView):
    form_class = LoginForm
    success_url = '/signin/gpg_auth/'
    template_name = "registration/login.html"

    def form_valid(self, form):
        request = self.request
        user = request.user
        users = User.objects.get(username=request.session['username'])
        if str(users.pgp_key) == "None":
            user = authenticate(request, username=request.session['username'], password=request.session['password'])
            login(request, user)
            msg = "Welcome back " + user.username.upper()
            messages.success(request, msg)
            self.success_url = "/"
        if not users.tfalogin:
            msg = "Welcome back " + user.username.upper()
            messages.success(request, msg)
            self.success_url = "/"
        return redirect(self.success_url)


# Use 2fa pgp login
def update_tfalogin(request):
    user = User.objects.get(username=request.session['username'])
    user.tfalogin = request.POST['login_method']
    user.save()
    messages.success(request, "Success")
    return redirect("user_profile")


# Vendor Public Profile View
def vendor_profile(request, vendor_id=None):
    message = len(Message.objects.filter(check=False))
    if request.method == 'GET' and vendor_id is not None or vendor_id is not "":
        vendor = User.objects.values('pgp_key').filter(id=vendor_id)
    else:
        raise Exception("404")

    context = {
        'user': vendor[0],
        'new_message': message
    }
    return render(request, 'profile/vendor_profile.html',context)


def vendor_public_profile(request, vendor_id=None):
    if request.method == 'POST':
        if VendorFavorite.objects.filter(Q(vendor_id=vendor_id) & Q(user=request.user)).count() == 0:
            obj = VendorFavorite()
            obj.vendor_id = vendor_id
            obj.user_id = request.user.id
            obj.save()

            vendor_user = User.objects.filter(Q(id=vendor_id))
            msg = "%s was added to my favorite" % vendor_user[0].username
            messages.success(request, msg)
        else:
            vendor_user = User.objects.filter(Q(id=vendor_id))
            msg = "%s was already added to my favorite" % vendor_user[0].username
            messages.success(request, msg)

    vendor_products = Product.objects.filter(productOwnerID=vendor_id)
    rating_dict = {}
    rating_total_sum = 0
    rating_count_sum = 0
    sold_cnt = {}
    sold_cnt_sum = 0

    for product in vendor_products:
        rating_dict[product.name] = product
        rating_total = 0
        rating_count = 0
        for order_item in product.order_items.filter(order__paid='8'):
            for rating in order_item.ratings.all():
                rating_total += rating.total * order_item.quantity
                rating_count += rating.count * order_item.quantity

        rating_total_sum += rating_total
        rating_count_sum += rating_count
        rating_dict[product.name] = 0 if rating_count == 0 else rating_total / rating_count
        sold_cnt[product.id] = product.order_items.filter(order__paid='8').aggregate(Sum('quantity'))['quantity__sum']
        sold_cnt[product.id] = 0 if sold_cnt[product.id] is None else sold_cnt[product.id]
        sold_cnt_sum += sold_cnt[product.id]

    vendor_user = VendorUser.objects.filter(id=vendor_id)
    vendor_term = VendorTerm.objects.filter(userId=vendor_id)
    crypto_data = crypto_currencies()

    context = {
        "vendor_user": vendor_user[0],
        "vendor_term": vendor_term[0].description,
        "vendor_rating": rating_total_sum/rating_count_sum if rating_count_sum != 0 else 0,
        "vendor_sold_count": sold_cnt_sum,
        "total_trusts": vendor_user[0].total_trusts(),
        "total_untrusts": vendor_user[0].total_untrusts(),
        "rating_dict": rating_dict,
        "crypto_data": crypto_data
    }
    return render(request, 'profile/vendor_public_profile.html', context)


def complete_order(request, order_id):
    order = Order.objects.filter(id=order_id)
    order.update(paid=8)
    pay = Pay.objects.filter(id=order.first().payment_id)
    pay.update(status=8)
    order_item = OrderItem.objects.filter(order_id=order_id)
    product_id = order_item.first().product_id
    product = Product.objects.filter(id=product_id)
    vendor_id = product.first().productOwnerID_id
    message_content = "Order are completed by customer."
    new_message = Message.objects.create(content=message_content, receiver=User.objects.get(id=vendor_id),
                                         sender=User.objects.get(username='admin'))
    new_message.save()
    msg = "Order are completed."
    # messages.add_message(request, 5, messages.SUCCESS, msg)
    messages.success(request, msg)
    return redirect('user_order_list')


def dispute_order(request, order_id):
    order = Order.objects.filter(id=order_id)
    order.update(paid=5)
    pay = Pay.objects.filter(id=order.first().payment_id)
    pay.update(status=5)
    order_item = OrderItem.objects.filter(order_id=order_id)
    product_id = order_item.first().product_id
    product = Product.objects.filter(id=product_id)
    vendor_id = product.first().productOwnerID_id
    message_content = "Customer require order to dispute. To dispute order can be approved by the staff. Please contact with staff."
    new_message = Message.objects.create(content=message_content, receiver=User.objects.get(id=vendor_id),
                                         sender=User.objects.get(username='admin'))
    new_message.save()
    msg = "Your dispute requirement have been sent to staff. To dispute order can be approved by the staff."
    # messages.add_message(request, 5, messages.SUCCESS, msg)
    messages.success(request, msg)
    return redirect('user_order_list')


def favorite_detail(request):
    favorites = VendorFavorite.objects.filter(Q(user=request.user))
    context_object = {'favorites': favorites}

    return render(request, 'profile/favorite_list.html', context_object)


def user_ratings(request):
    order_items = OrderItem.objects.filter(Q(product__productOwnerID=request.user, order__paid='8'))
    context_object = {'order_items': order_items}
    return render(request, 'profile/ratings.html', context_object)


def vendor_stats(request):
    if request.method == 'POST':
        btc_course = (requests.get("https://api.coindesk.com/v1/bpi/currentprice/USD.json").json())["bpi"]['USD']["rate_float"]
        usd_price = 1
        btc_price = round((float(usd_price) / float(btc_course)), 8)
        rpc_user = "NSA12012"
        rpc_password = "ZIwnhqsa"
        rpc_connection = AuthServiceProxy("http://%s:%s@213.227.140.1:8332" % (rpc_user, rpc_password))
        address = rpc_connection.getnewaddress()

        pay = Pay.objects.create(timestamp=timezone.now(), btc_course=btc_course, amount_expected=btc_price,
                                 amount_received=0, author=request.user.username, status=0, address=address)
        pay.save()

        order = Order.objects.create(address="upgrade_vendor__", user=request.user, payment=pay, paid="1")
        order.save()

        # content = "Will send you message after confirm your transaction. Please wait some times during confirm your transaction."
        # return render(request, "orders/order/waiting.html", {'content': content})
        return render(request, 'orders/order/pay.html',
                    {'order_id': order.id, 'address': address, 'btc_course': btc_course, "total_price": usd_price,
                    "btc_price": btc_price})

    elif request.method == 'GET':
        return render(request, 'profile/vendor_stats.html')


# this function to update terms and conditions of the User
def change_terms(request):
    pass


def trust_vendor(request):
    vendor_user = get_object_or_404(User, id=request.POST.get('vendor_id'))
    if vendor_user.id != request.user.id:
        vendor_user.untrusts.remove(request.user)
        vendor_user.trusts.add(request.user)
    next_page = request.POST.get('next', '/')
    return HttpResponseRedirect(next_page)


def untrust_vendor(request):
    vendor_user = get_object_or_404(User, id=request.POST.get('vendor_id'))
    if vendor_user.id != request.user.id:
        vendor_user.trusts.remove(request.user)
        vendor_user.untrusts.add(request.user)
    next_page = request.POST.get('next', '/')
    return HttpResponseRedirect(next_page)


def comment_order_item(request):
    order_item = get_object_or_404(OrderItem, id=request.POST.get('order_item_id'))
    order_item.comment = request.POST.get('comment')
    order_item.save()
    next_page = request.POST.get('next', '/')
    return HttpResponseRedirect(next_page)
