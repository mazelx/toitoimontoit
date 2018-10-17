import random
import logging
from urllib.request import urlopen
import requests
from PIL import Image
from imagehash import phash, hex_to_hash
from peewee import DoesNotExist
from models import Annonce
from trello_module import TrelloModule


class Search:
    HASH_SIMILAR_TRESHOLD = 8

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
                    proxy_index = self.__next_proxy_index(proxy_index)
                else:
                    break
        raise ConnectionError("Cannot connect to API")

    def save(self, uid, site, created, title, city, link, price, surface,
             description=None, telephone=None, rooms=None, bedrooms=None, picture=None):
        is_duplicate = False
        similar_ad = None

        # ad already exists ?
        try:
            Annonce.get_by_id(uid)
            return False
        except DoesNotExist:
            pass

        # ad exists as similar ad ?
        for pic in picture:
            similar_ad = self.__find_similar_ad_from_pic(pic)
            if similar_ad:
                logging.info(
                    "(" + site + ") ad for " + title + " already exists : " +
                    link + " = " + similar_ad.link
                )
                is_duplicate = True
                if similar_ad.posted2trello:
                    TrelloModule().add_new_link(similar_ad, link)
                    break
                else:
                    # the similar ad is not yet on trello, will process and save this similar ad the next launch
                    return False

        annonce = Annonce.create(
            id=uid,
            site=site,
            created=created,
            title=title,
            description=description,
            telephone=telephone,
            price=price,
            surface=surface,
            rooms=rooms,
            bedrooms=bedrooms,
            city=city,
            link=link,
            picture=picture,
            picturehash=phash(Image.open(urlopen(picture[0]))) if len(picture) > 0 else None,
            posted2trello=is_duplicate,
            isduplicate=is_duplicate,
            trelloid=similar_ad.idtrello if similar_ad else None
        )

        logging.info("(" + site + ") new ad saved : " + title + ("(duplicate)" if is_duplicate else ""))
        annonce.save()
        return True

    def __next_proxy_index(self, proxy_index):
        self.proxies.pop(proxy_index)
        if len(self.proxies) == 0:
            return -1
        return random.randint(0, len(self.proxies) - 1)

    def __find_similar_ad_from_pic(self, picture):
        new_hash = phash(Image.open(urlopen(picture)))
        hashes = [ad.picturehash for ad in Annonce.select()]
        for old_hash in hashes:
            if (hex_to_hash(old_hash) - new_hash) < self.HASH_SIMILAR_TRESHOLD:
                return Annonce.get(Annonce.picturehash == old_hash)


