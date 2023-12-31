from datetime import timedelta

from requests_cache import CachedSession

from logs.log import log

from secret import CAT_KEY

class CatApi:

    source = "The Cat Api"

    @classmethod
    def extract(cls) -> str:
        try:
            response = CachedSession("api-cache", expire_after=timedelta(hours=4)).get(f"https://api.thecatapi.com/v1/images/search?limit=1&api_key={CAT_KEY}")
        except Exception as err:
            log(err)
            return {
                'url': "attachment://bot_icon.jpg",
                'source': cls.source
            }

        if response.status_code == 200:
            return {
                'url': response.json()[0]['url'],
                'source': cls.source
            }