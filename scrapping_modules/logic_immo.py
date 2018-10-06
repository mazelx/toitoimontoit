from pprint import pprint

import requests
from datetime import datetime
from models import Annonce

"""Module qui récupère les annonces de Logic-Immo"""

header = {
    'User-Agent': 'logicimmo-android/8.5.1',
    'Connection': 'Keep-Alive',
    'Accept-Encoding': 'gzip'
}


def search(parameters):
    # Préparation des paramètres de la requête
    payload = {
        'client': "v8.a.3",
    }
    if parameters.get('price'):
        payload['price_range'] = "%s,%s" % (parameters['price'][0], parameters['price'][1])  # Loyer

    if parameters.get('surface'):
        payload['area_range'] = "%s,%s" % (parameters['surface'][0], parameters['surface'][1])  # Surface

    if parameters.get('rooms'):
        payload['rooms_range'] = "%s,%s" % (parameters['rooms'][0], parameters['rooms'][1])  # Pièces

    if parameters.get('bedrooms'):
        payload['bedrooms_range'] = "%s,%s" % (parameters['bedrooms'][0], parameters['bedrooms'][1])  # Chambres

    if parameters.get('cities'):
        payload['localities'] = ','.join(key for key in search_city_code(parameters['cities']))

    # Insertion des paramètres propres à LeBonCoin
    payload.update(parameters['logic-immo'])

    request = requests.post("http://lisemobile.logic-immo.com/li.search_ads.php", params=payload, headers=header)
    data = request.json()

    for ad in data['items']:

        annonce, created = Annonce.get_or_create(
            id='logic-immo-' + ad['identifiers']['main'],
            defaults={
                'site': "Logic Immo",
                'created': datetime.fromtimestamp(ad['info'].get('firstOnlineDate')),
                'title': "%s %s pièces" % (ad['info']['propertyType'].get('name'), ad['properties'].get('rooms')),
                'description': ad['info'].get('text'),
                'telephone': ad['contact'].get('phone'),
                'price': ad['pricing']['amount'],
                'surface': ad['properties'].get('area'),
                'rooms': ad['properties'].get('rooms'),
                'bedrooms': ad['properties'].get('bedrooms'),
                'city': ad['location']['city']['name'],
                'link': ad['info']['link'],
                'picture': [get_picture(picture) for picture in ad.get('pictures')]
            }
        )
        if created:
            annonce.save()


def search_city_code(cities):
    keys = list()

    for city in cities:
        payload = {
            'client': "v8.a",
            'fulltext': city[1]
        }

        request = requests.post("http://lisemobile.logic-immo.com/li.search_localities.php", params=payload,
                                headers=header)
        data = request.json()
        keys.append(data['items'][0]['key'])

    return keys


def get_picture(url):
    r = requests.get(url.replace("[WIDTH]", "1440").replace("[HEIGHT]", "956").replace("[SCALE]", "3.5"))
    return r.url

