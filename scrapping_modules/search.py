import random
import logging
import requests
from models import Annonce

# TODO: divide search and save and display log between them
from requests import ConnectTimeout
from urllib3.exceptions import HTTPError, TimeoutError, ProxyError


class Search:
    def __init__(self, parameters, proxies=[]):
        self.proxies = proxies
        self.parameters = parameters
        self.header = ""

    def request(self, method, url, params=None, data=None):
        proxy_index = 0
        # change proxy in case of connection error
        while True:
            proxy_dict = None
            if self.proxies:
                proxy_dict = {'http': self.proxies[proxy_index], 'https': self.proxies[proxy_index]}
            try:
                response = requests.request(method,
                                            url,
                                            params=params,
                                            data=data,
                                            headers=self.header,
                                            proxies=proxy_dict,
                                            timeout=5)
                # got 200 code
                if response.ok:
                    return response
                # got HTTP error code (40X,50X...)
                if self.proxies:
                    raise Exception()
                break

            except Exception as e:
                if self.proxies:
                    logging.info("Error connecting to API with proxy : " + self.proxies[proxy_index])
                    logging.debug("Error : " + e.__str__())
                    proxy_index = self.next_proxy_index(proxy_index)
                else:
                    break
        raise ConnectionError("Cannot connect to API")

    def save(self, uid, site, created, title, city, link, price, surface,
             description=None, telephone=None, rooms=None, bedrooms=None, picture=None):
        annonce, created = Annonce.get_or_create(
            id=uid,
            defaults={
                'site': site,
                'created': created,
                'title': title,
                'description': description,
                'telephone': telephone,
                'price': price,
                'surface': surface,
                'rooms': rooms,
                'bedrooms': bedrooms,
                'city': city,
                'link': link,
                'picture': picture
            })

        if created:
            logging.info("(" + site + ") new ad saved : " + title)
            annonce.save()



    def next_proxy_index(self, proxy_index):
        self.proxies.pop(proxy_index)
        if len(self.proxies) == 0:
            return -1
        return random.randint(0, len(self.proxies) - 1)
