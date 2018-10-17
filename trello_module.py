import json
from trello import TrelloClient, ResourceUnavailable
from models import Annonce
from ast import literal_eval
import logging


class TrelloModule:
    def __init__(self):
        with open("trello.json") as parameters_data:
            self.config = json.load(parameters_data)

        self.trello = TrelloClient(
            api_key=self.config['ApiKey'],
            api_secret=self.config['ApiSecret'],
            token=self.config['Token'],
            token_secret=self.config['TokenSecret']
        )

    def get_board(self):
        '''
        Retourne la liste Trello indiquée dans trello.ini
        '''

        # Chargement des paramètres et identifiants Trello depuis le fichier JSON
        for b in self.trello.list_boards():
            if b.name == self.config['BoardName']:
                return b

        print("Board " + self.config['BoardName'] + " not found.")
        exit()

    def get_list(self, site):
        board = self.get_board()

        for l in board.all_lists():
            if l.name == site:
                return l

        # Liste pas trouvée, on la crée
        return board.add_list(site)

    def post(self):
        '''
        Poste les annonces sur Trello
        '''
        posted = 0

        for annonce in Annonce.select().where(Annonce.posted2trello == False).order_by(Annonce.site.asc()):
            title = "%s de %sm² à %s @ %s€" % (annonce.title, annonce.surface, annonce.city, annonce.price)
            description = "Créé le : %s\n\n" \
                          "%s pièces, %s chambre(s)\n" \
                          "Tel : %s\n\n" % \
                          (annonce.created.strftime("%a %d %b %Y %H:%M:%S"), annonce.rooms, annonce.bedrooms,
                           annonce.telephone)
            if annonce.description is not None:
                description += ">%s" % annonce.description.replace("\n", "\n>")

            card = self.get_list(annonce.site).add_card(title, desc=description)

            # On s'assure que ce soit bien un tableau
            if annonce.picture is not None and annonce.picture.startswith("["):
                # Conversion de la chaîne de caractère représentant le tableau d'images en tableau
                for picture in literal_eval(annonce.picture):
                    card.attach(url=picture)
                # Il n'y a qu'une photo
            elif annonce.picture is not None and annonce.picture.startswith("http"):
                card.attach(url=annonce.picture)

            card.attach(url=annonce.link)

            annonce.posted2trello = True
            annonce.idtrello = card.id
            annonce.save()
            posted += 1
        return posted

    def add_new_link(self, annonce, link):
        try:
            if not annonce.idtrello:
                raise ReferenceError
            card = self.trello.get_card(annonce.idtrello)
            card.attach(url=link)
        except (ResourceUnavailable, ReferenceError):
            logging.error("Trello card not found ( " + annonce.title + " : " + annonce.link + ")")

