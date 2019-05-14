from bitcoinrpc.authproxy import AuthServiceProxy
import sqlite3
from datetime import datetime
import time
import os
import django
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dark-web-master.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "dark_web.settings"
django.setup()
from orders.models import Pay, Order, OrderItem
from main.models import Message
from accounts.models import User

db_conn = sqlite3.connect("db.sqlite3")
q_conn = db_conn.cursor()

rpc_user = "NSA12012"
rpc_password = "ZIwnhqsa"

q_conn.execute("select id, payment_id, user_id, address from orders_order where paid='1' and payment_id!='0'")
order_list = q_conn.fetchall()

for order in order_list:
    order_id = order[0]
    payment_id = order[1]
    user_id = order[2]
    order_address = order[3]

    q_conn.execute("select address, amount_expected, amount_received from orders_pay where id={payment_id}".format(payment_id=payment_id))
    payment_info_list = q_conn.fetchall()
    if len(payment_info_list) > 1:
        pass

    address = payment_info_list[0][0]
    cost = payment_info_list[0][1]
    receive = payment_info_list[0][2]

    rpc_connection = AuthServiceProxy("http://%s:%s@213.227.140.1:8332" % (rpc_user, rpc_password))
    rec = rpc_connection.getreceivedbyaddress(address)

    if float(rec) > 0:
        if float(rec) >= float(cost):
            # print("find confirmed transaction")
            # file = open("log.txt", "a")
            # file.write("find confirmed transaction---%s" % str(datetime.now()))
            transaction = Pay.objects.filter(address=address)
            fee_amount = str(round(float(rec) * 3 / 100, 8))
            vendor_amount = str(float(rec) - float(fee_amount))
            transaction.update(status=2, amount_received=rec, vendor_amount=vendor_amount, fee_amount=fee_amount)
            order = Order.objects.filter(id=order_id)
            order.update(paid="2")
            message_content = "Your payment are confirmed. Thank you."
            message_obj = Message.objects.create(content=message_content, receiver_id=user_id, sender_id="1")

            # Upgrade to Vendor
            q_conn.execute("select id from orders_orderitem where order_id={order_id}".format(order_id=order_id))
            order_items = q_conn.fetchall()
            if order_address == 'upgrade_vendor__' and len(order_items) == 0:
                user = User.objects.filter(id=user_id)
                user.update(vendor=True)
            # q_conn.execute("insert into `main_message` (`content`, `create`, `update`, `receiver_id`, `sender_id`) VALUES ('{content}', '{receiver}', '{sender}')".format(content=message_content, receiver=user_id, sender="1"))
            # db_conn.commit()
        else:
            #print("find unconfirmed transaction.")
            transaction = Pay.objects.filter(address=address)
            transaction.update(timesamp=datetime.now())
            order = Order.objects.filter(id=order_id)
            order.update(updated=datetime.now())
            message_content = "Products price are {cost}BTC but you paid {rec}BTC. Please pay rest amount."
            message_obj = Message.objects.create(content=message_content, receiver_id=user_id, sender_id="1")
            #q_conn.execute("insert into `main_message` (`content`, `receiver_id`, `sender_id`) VALUES ('{content}', '{receiver}', '{sender}')".format(content=message_content, receiver=user_id, sender="1"))
            #db_conn.commit()



db_conn.close()
print("One period of Scanning Transaction are finished.")
time.sleep(3)