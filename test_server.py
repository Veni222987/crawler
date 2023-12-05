from unittest import TestCase

from server import check_and_return_json


class Test(TestCase):
    def test_check_and_return_json(self):
        data = check_and_return_json("output/广州.json")
        print(data)
