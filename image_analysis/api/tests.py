import json
import pathlib
from django.test import TestCase
from api.views import get_top_labels

# Create your tests here.
class ViewsTestCase(TestCase):
    test_json_path = (
        str(pathlib.Path(__file__).parent.resolve()) + "/resources/test.json"
    )

    def test_get_top_labels(self):
        f = open(ViewsTestCase.test_json_path)
        hit_array = json.load(f)["hits"]["hits"]
        get_top_labels(hit_array)
