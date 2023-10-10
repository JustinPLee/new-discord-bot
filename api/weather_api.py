from datetime import timedelta

from requests_cache import CachedSession

from logs.log import log

from secret import WEATHER_KEY, WEATHER_BASE

class WeatherApi:

    source = "Open Weather Api"

    @staticmethod
    def request_data(location: str) -> str:
        assert location != ""

        try:
            response = CachedSession("api-cache", expire_after=timedelta(hours=4)).get(url=f"{WEATHER_BASE}/forecast.json?key={WEATHER_KEY}&q={location}&days=1")
        except Exception as err:
            log(err)
            raise Exception("error retrieiving weather data")

        if response.status_code == 200:
            return response.json()

    @classmethod
    def extract(cls, **kwargs) -> {}:
        try:
            data = cls.request_data(kwargs['location'])
        except Exception as err:
            return {}

        # return relevant data
        path = data['forecast']['forecastday'][0]['day']
        return {
            'highest_temperature': path['maxtemp_f'],
            'wind': path['maxwind_mph'],
            'rain': path['daily_chance_of_rain'],
            'summary': path['condition']['text'],
            'icon': path['condition']['icon'],
            'location': data['location']['name'],
            'source': cls.source
        }

    # helper function
    @staticmethod
    def location_exists(location: str) -> bool:
        return WeatherApi.request_data(location=location) is not None