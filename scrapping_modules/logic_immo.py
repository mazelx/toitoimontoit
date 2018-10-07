import logging

from scrapping_modules.search import Search
from datetime import datetime
from models import Annonce

"""Module qui récupère les annonces de Logic-Immo"""


class LogicImmoSearch(Search):
    def __init__(self, parameters, proxies):
        super().__init__(parameters, proxies)
        self.header = {
                        'User-Agent': 'logicimmo-android/8.5.1',
                        'Connection': 'Keep-Alive',
                        'Accept-Encoding': 'gzip'
                        }

    def search(self):
        # Préparation des paramètres de la requête
        payload = {
            'client': "v8.a.3",
        }

        if self.parameters.get('price'):
            payload['price_range'] = "%s,%s" % (self.parameters['price'][0], self.parameters['price'][1])  # Loyer

        if self.parameters.get('surface'):
            payload['area_range'] = "%s,%s" % (self.parameters['surface'][0], self.parameters['surface'][1])  # Surface

        if self.parameters.get('rooms'):
            payload['rooms_range'] = "%s,%s" % (self.parameters['rooms'][0], self.parameters['rooms'][1])  # Pièces

        if self.parameters.get('bedrooms'):
            payload['bedrooms_range'] = "%s,%s" % (self.parameters['bedrooms'][0], self.parameters['bedrooms'][1])  # Chambres

        if self.parameters.get('cities'):
            payload['localities'] = ','.join(key for key in self.search_city_code(self.parameters['cities']))

        # Insertion des paramètres propres à LeBonCoin
        payload.update(self.parameters['logic-immo'])

        request = self.request(method="POST",
                               url="http://lisemobile.logic-immo.com/li.search_ads.php",
                               params=payload
                               )
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
                    'picture': [self.get_picture(picture) for picture in ad.get('pictures')]
                }
            )
            if created:
                annonce.save()

    def search_city_code(self, cities):
        keys = list()

        for city in cities:
            payload = {
                'client': "v8.a",
                'fulltext': city[1]
            }

            request = self.request(method="GET",
                                   url="http://lisemobile.logic-immo.com/li.search_localities.php",
                                   params=payload)
            data = request.json()
            keys.append(data['items'][0]['key'])

        return keys

    def get_picture(self, url):
        r = self.request(method="GET",
                         url=url.replace("[WIDTH]", "1440").replace("[HEIGHT]", "956").replace("[SCALE]", "3.5"))
        return r.url

