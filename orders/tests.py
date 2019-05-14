from django.test import TestCase
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
# Create your tests here.

rpc_user = "NSA12012"
rpc_password = "ZIwnhqsa"
rpc_connection = AuthServiceProxy("http://%s:%s@213.227.140.1:8332" % (rpc_user, rpc_password))
rec = rpc_connection.getreceivedbyaddress("3PX9dSd2TBcxsHJ6y3CXtQiMJnPtpYVrqc")
balance = rpc_connection.getbalance()
transaction_list = rpc_connection.listtransactions()
print(rec)


