from scrapping_modules.search import Search
from urllib.parse import unquote, urlencode
from datetime import datetime
from models import Annonce

"""Module qui récupère les annonces de PAP"""


class PAPSearch(Search):
    def __init__(self, parameters, proxies):
        super().__init__(parameters, proxies)
        self.header = {
                      'X-Device-Gsf': '36049adaf18ade77',
                      'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; D5803 Build/MOB30M.Z1)',
                      'Connection': 'Keep-Alive',
                      'Accept-Encoding': 'gzip'
                      }

    def search(self):
        # Préparation des paramètres de la requête
        payload = {
            'size': 200,
            'page': 1
        }

        if self.parameters.get('price'):
            payload['recherche[prix][min]'] = self.parameters['price'][0]  # Loyer min
            payload['recherche[prix][max]'] = self.parameters['price'][1]  # Loyer max

        if self.parameters.get('surface'):
            payload['recherche[surface][min]'] = self.parameters['surface'][0]  # Surface min
            payload['recherche[surface][max]'] = self.parameters['surface'][1]  # Surface max

        if self.parameters.get('rooms'):
            payload['recherche[nb_pieces][min]'] = self.parameters['rooms'][0]  # Pièces min

        if self.parameters.get('bedrooms'):
            payload['recherche[nb_chambres][min]'] = self.parameters['bedrooms'][0]  # Chambres min

        if self.parameters.get('cities'):
            payload['zipcode'] = ','.join(str(cp[1]) for cp in self.parameters['cities'])
            payload['city'] = ','.join(cp[0] for cp in self.parameters['cities'])

        # Insertion des paramètres propres à PAP
        payload.update(self.parameters['pap'])

        params = urlencode(payload)

        # Ajout des villes
        for city in self.parameters['cities']:
            params += "&recherche[geo][ids][]=%s" % self.place_search(city[1])

        request = self.request(method="GET",
                               url="https://ws.pap.fr/immobilier/annonces",
                               params=unquote(params))
        data = request.json()

        for ad in data['_embedded']['annonce']:
            _request = self.request(method="GET",
                                    url="https://ws.pap.fr/immobilier/annonces/%s" % ad['id'])
            _data = _request.json()

            photos = list()
            if _data.get("nb_photos") > 0:
                for photo in _data["_embedded"]['photo']:
                    photos.append(photo['_links']['self']['href'])

            self.save(
                    uid='pap-%s' % _data.get('id'),
                    site="PAP",
                    title="%s %s pièces" % (_data.get("typebien"), _data.get("nb_pieces")),
                    description=str(_data.get("texte")),
                    telephone=_data.get("telephones")[0].replace('.', '') if len(_data.get("telephones")) > 0 else None,
                    created=datetime.fromtimestamp(_data.get("date_classement")),
                    price=_data.get('prix'),
                    surface=_data.get('surface'),
                    rooms=_data.get('nb_pieces'),
                    bedrooms=_data.get('nb_chambres_max'),
                    city=_data["_embedded"]['place'][0]['title'],
                    link=_data["_links"]['desktop']['href'],
                    picture=photos
            )

    def place_search(self, zipcode):
        """Retourne l'identifiant PAP pour un code postal donné"""

        payload = {
            "recherche[cible]": "pap-recherche-ac",
            "recherche[q]": zipcode
        }

        request = self.request(method="GET",
                               url="https://ws.pap.fr/gis/places",
                               params=payload)
        return request.json()['_embedded']['place'][0]['id']