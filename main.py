import os
import sys
import json
import requests
import models
import trello_module
import logging
from bs4 import BeautifulSoup
from scrapping_modules.logic_immo import LogicImmoSearch
from scrapping_modules.seloger import SeLogerSearch
from scrapping_modules.leboncoin import LeBonCoinSearch
from scrapping_modules.pap import PAPSearch


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s :: %(levelname)s :: %(message)s')

    os.chdir(os.path.dirname(sys.argv[0]))
    models.create_tables()

    # Chargement des paramètres de recherche depuis le fichier JSON
    with open("parameters.json", encoding='utf-8') as parameters_data:
        parameters = json.load(parameters_data)

    # get proxies
    proxies = []
    if parameters['use-proxy']:
        proxies = get_proxies()

    # Recherche et insertion en base
    if "logic_immo" in parameters['ad-providers']:
        try :
            logging.info("Retrieving from logic_immo")
            LogicImmoSearch(parameters, proxies).search()
        except ConnectionError:
            logging.error("Error while retrieving from logic_immo")

    if "seloger" in parameters['ad-providers']:
        try:
            logging.info("Retrieving from seloger")
            SeLogerSearch(parameters, proxies).search()
        except ConnectionError:
            logging.error("Error while retrieving from seloger")

    if "leboncoin" in parameters['ad-providers']:
        try:
            logging.info("Retrieving from leboncoin")
            LeBonCoinSearch(parameters, proxies).search()
        except ConnectionError:
            logging.error("Error while retrieving from leboncoin")

    if "pap" in parameters['ad-providers']:
        try:
            logging.info("Retrieving from pap")
            PAPSearch(parameters, proxies).search()
        except ConnectionError:
            logging.error("Error while retrieving from pap")

    # Envoi des annonces sur Trello
    posted = trello_module.post()
    logging.info("%s new ads posted to Trello" % posted)


def get_proxies():
    # Retrieve latest proxies
    proxies = []
    response = requests.get('https://www.sslproxies.org/')
    soup = BeautifulSoup(response.text, 'html.parser')
    proxies_table = soup.find(id='proxylisttable')

    # Save proxies in the array
    for row in proxies_table.tbody.find_all('tr'):
        proxies.append(
            'http://' + row.find_all('td')[0].string + ":" + row.find_all('td')[1].string
        )
    return proxies[:10]

if __name__ == "__main__":
    # execute only if run as a script
    main()