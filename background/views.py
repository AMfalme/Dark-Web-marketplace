from django.shortcuts import render
from background_task import background
from cryptowatch_client import Client
from .models import CryptoCurrencies


def pull_crypto_price(request):
    run_background_pull_crypto_price()
    return render(request, 'pull_crypto_price.html', {})


@background(schedule=0)
def run_background_pull_crypto_price():
    try:
        print('run task')
        crypto_price = get_crypto_currencies_prices()
        print(crypto_price)

        for coin, price in crypto_price.items():
            obj, created = CryptoCurrencies.objects.update_or_create(
                name=coin,
                defaults={'price': price, 'name': coin},
            )
            print('create or update ', coin, ' with price ', price)

        print('process done')
    except Exception as e:
        print(e)


def get_crypto_currencies_prices():
    btcgbp_price = 0
    btcusd_price = 0
    btceur_price = 0
    try:
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
    except Exception as e:
        pass
    crypto_price = {'btcusd': btcusd_price, 'btcgbp': btcgbp_price, 'btceur': btceur_price}
    return crypto_price


def crypto_currencies():
    crypto_price = {'btcusd': 0, 'btcgbp': 0, 'btceur': 0}
    try:
        coins_from_db = CryptoCurrencies.objects.all()
        for row in coins_from_db:
            crypto_price[row.name] = row.price
    except Exception as e:
        pass
    return crypto_price

