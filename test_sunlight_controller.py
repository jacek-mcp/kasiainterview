import unittest
import requests
from pprint import pprint

BASE = "http://127.0.0.1:5000/"

# TODO utwórz generator jsonów
JSON = {"city_data":
            [
                {
                    "name": "gracia",
                    "apartments_height": 2.34,
                    "buildings":
                        [
                            {
                                "name": "la",
                                "apartments_count": 7,
                                "distance": 0
                            },
                            {
                                "name": "si",
                                "apartments_count": 3,
                                "distance": 25
                            }
                        ]
                },
                {
                    "name": "example",
                    "apartments_height": 2.50,
                    "buildings":
                        [
                            {
                                "name": "do",
                                "apartments_count": 12,
                                "distance": 0
                            }
                        ]
                }
            ]
}


# TODO Kasia: dodaj testy

class TestCityController(unittest.TestCase):

    def test_post(self):
        response = requests.post(BASE + "sunlightAPI/barcelona", json=JSON)
        print(response)

    def test_get(self):
        response = requests.get(BASE + "sunlightAPI/barcelona")
        print(response)


class TestSunlightController(unittest.TestCase):

    def test_get(self):
        response = requests.get(BASE + "sunlightAPI/barcelona/gracia/la/3")
        print(response)

if __name__ == '__main__':
    unittest.main()
