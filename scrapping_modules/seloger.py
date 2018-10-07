from scrapping_modules.search import Search
import xml.etree.ElementTree as ET
from datetime import datetime
'''Module qui récupère les annonces de SeLoger.com'''


class SeLogerSearch(Search):
    def __init__(self, parameters, proxies):
        super().__init__(parameters, proxies)
        self.header = {'user-agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; D5803 Build/MOB30M.Z1)'}

    def search(self):
        # Préparation des paramètres de la requête
        payload = {}

        if self.parameters.get('price'):
            payload['pxmin'] = self.parameters['price'][0]  # Loyer min
            payload['pxmax'] = self.parameters['price'][1]  # Loyer max

        if self.parameters.get('surface'):
            payload['surfacemin'] = self.parameters['surface'][0]  # Surface min
            payload['surfacemax'] = self.parameters['surface'][1]  # Surface max

        if self.parameters.get('rooms'):
            payload['nbpieces'] = list(range(self.parameters['rooms'][0], self.parameters['rooms'][1] + 1))

        if self.parameters.get('bedrooms'):
            payload['nb_chambres'] = list(range(self.parameters['bedrooms'][0], self.parameters['bedrooms'][1] + 1))

        if self.parameters.get('cities'):
            payload['ci'] = [int(cp[2]) for cp in self.parameters['cities']]

        # Insertion des paramètres propres à SeLoger
        payload.update(self.parameters['seloger'])

        request = self.request(method="GET",
                               url="http://ws.seloger.com/search.xml",
                               params=payload)

        xml_root = ET.fromstring(request.text)

        for annonceNode in xml_root.findall('annonces/annonce'):
            # Seconde requête pour obtenir la description de l'annonce
            _payload = {'noAudiotel': 1, 'idAnnonce': annonceNode.findtext('idAnnonce')}
            _request = self.request(method="GET",
                                    url="http://ws.seloger.com/annonceDetail.xml",
                                    params=_payload)

            photos = list()
            for photo in annonceNode.find("photos"):
                photos.append(photo.findtext("stdUrl"))

            # SeLoger peut ne pas fournir de titre pour une annonce T_T
            title = "Appartement " + annonceNode.findtext('nbPiece') + " pièces" \
                if annonceNode.findtext('titre') is None \
                else annonceNode.findtext('titre')

            self.save(
                uid='seloger-' + annonceNode.find('idAnnonce').text,
                site='SeLoger',
                title=title,
                description=ET.fromstring(_request.text).findtext("descriptif"),
                telephone=ET.fromstring(_request.text).findtext("contact/telephone"),
                created=datetime.strptime(annonceNode.findtext('dtCreation'), '%Y-%m-%dT%H:%M:%S'),
                price=annonceNode.find('prix').text if annonceNode.find('prix') is not None else None,
                surface=annonceNode.find('surface').text if annonceNode.find('surface') is not None else None,
                rooms=annonceNode.find('nbPiece').text if annonceNode.find('nbPiece') is not None else None,
                bedrooms=annonceNode.find('nbChambre').text if annonceNode.find('nbChambre') is not None else None,
                city=annonceNode.findtext('ville'),
                link=annonceNode.findtext('permaLien'),
                picture=photos
            )