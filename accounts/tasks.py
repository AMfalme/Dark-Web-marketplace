
from __future__ import absolute_import, unicode_literals
from .celery import app
from .models import User
from orders.models import Pay
from bitcoinrpc.authproxy import AuthServiceProxy


@app.task
def add(x, y):
    return x + y


@app.task
def update(address, cost, user_id):
    rpc_user = "NSA12012"
    rpc_password = "ZIwnhqsa"
    rpc_connection = AuthServiceProxy("http://%s:%s@213.227.140.1:8332" % (rpc_user, rpc_password))

    transaction = Pay.objects.filter(address=address)
    rec = rpc_connection.getreceivedbyaddress(address)

    if float(rec) == float(cost):
        transaction.update(status=2, amount_received=rec)
        user = User.objects.filter(id=user_id)
        user.update(vendor=True)
        return "thanks you have paid"
    else:
        transaction.update(status=1, amount_received=rec)
