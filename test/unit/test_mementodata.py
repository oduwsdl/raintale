import unittest
import os
import pprint

from raintale.surrogatedata import MementoData

testdir = os.path.dirname(os.path.realpath(__file__))

pp = pprint.PrettyPrinter(indent=4)

class TestMementoData(unittest.TestCase):

    def test_simple_template(self):
        pass

    def test_complex_template(self):

        urim1 = "http://archive.example/20100424130000/https://example.com"
        urim2 = "http://archive.example/20150714130000/https://example2.com"
        mementoembed_api = "http://127.0.0.1:9899/shouldnotwork" # should go nowhere

        with open("{}/test_template.html".format(testdir)) as f:
            template_str = f.read()

        expected_data = {}

        for urim in [ urim1, urim2 ]:
            updated_data = {
                ( "{{ element.surrogate.image|prefer rank=1 }}", urim ): {
                    "endpoint path": "/services/memento/imagedata/",
                    "full endpoint": "{}/services/memento/imagedata/{}".format(mementoembed_api, urim),
                    "MementoEmbed preferences": (),
                    "Raintale preferences": ( "rank=1", ),
                    "sanitized field name": "image__prefer__rank_1",
                    "base field name": "image"
                },
                ( "{{ element.surrogate.image|prefer rank=2 }}", urim ): {
                    "endpoint path": "/services/memento/imagedata/",
                    "full endpoint": "{}/services/memento/imagedata/{}".format(mementoembed_api, urim),
                    "MementoEmbed preferences": (),
                    "Raintale preferences": ( "rank=2", ),
                    "sanitized field name": "image__prefer__rank_2",
                    "base field name": "image"
                },
                ( "{{ element.surrogate.image|prefer rank=3 }}", urim ): {
                    "endpoint path": "/services/memento/imagedata/",
                    "full endpoint": "{}/services/memento/imagedata/{}".format(mementoembed_api, urim),
                    "MementoEmbed preferences": (),
                    "Raintale preferences": ( "rank=3", ),
                    "sanitized field name": "image__prefer__rank_3",
                    "base field name": "image"
                },
                ( "{{ element.surrogate.image|prefer rank=4,datauri=yes }}", urim ): {
                    "endpoint path": "/services/memento/imagedata/",
                    "full endpoint": "{}/services/memento/imagedata/{}".format(mementoembed_api, urim),
                    "MementoEmbed preferences": (),
                    "Raintale preferences": ( "rank=4", "datauri=yes" ),
                    "sanitized field name": "image__prefer__rank_4_datauri_yes",
                    "base field name": "image"
                },
                ( "{{ element.surrogate.urim }}", urim ): {
                    "endpoint path": None,
                    "full endpoint": None,
                    "MementoEmbed preferences": (),
                    "Raintale preferences": (),
                    "sanitized field name": "urim",
                    "base field name": "urim"
                },
                ( "{{ element.surrogate.original_favicon|prefer datauri_favicon=yes }}", urim ): {
                    "endpoint path": "/services/memento/originalresourcedata/",
                    "full endpoint": "{}/services/memento/originalresourcedata/{}".format(mementoembed_api, urim),
                    "MementoEmbed preferences": ( "datauri_favicon=yes", ),
                    "Raintale preferences": (),
                    "sanitized field name": "original_favicon__prefer__datauri_favicon_yes",
                    "base field name": "original_favicon"
                },
                ( "{{ element.surrogate.archive_favicon|prefer datauri_favicon=yes }}", urim ): {
                    "endpoint path": "/services/memento/archivedata/",
                    "full endpoint": "{}/services/memento/archivedata/{}".format(mementoembed_api, urim),
                    "MementoEmbed preferences": ( "datauri_favicon=yes", ),
                    "Raintale preferences": (),
                    "sanitized field name": "archive_favicon__prefer__datauri_favicon_yes",
                    "base field name": "archive_favicon"
                },
                ( "{{ element.surrogate.archive_uri }}", urim ): {
                    "endpoint path": "/services/memento/archivedata/",
                    "full endpoint": "{}/services/memento/archivedata/{}".format(mementoembed_api, urim),
                    "MementoEmbed preferences": (),
                    "Raintale preferences": (),
                    "sanitized field name": "archive_uri",
                    "base field name": "archive_uri"
                }
            }
            expected_data.update(updated_data)

        md = MementoData(template_str, mementoembed_api)

        md.add(urim1)
        md.add(urim2)

        # pp.pprint(md._template_surrogate_fields)
        # pp.pprint(md._data)

        for fieldname, urim in expected_data:

            self.assertEqual(
                expected_data[ (fieldname, urim) ]["endpoint path"], 
                md._data[ (fieldname, urim) ]["endpoint path"],
                "failed to match 'endpoint path' for {},{}".format(fieldname, urim)
                )

            self.assertEqual(
                expected_data[ (fieldname, urim) ]["full endpoint"],
                md._data[ (fieldname, urim) ]["full endpoint"],
                "failed to match 'full endpoint' for {},{}".format(fieldname, urim)
                )

            self.assertEqual(
                expected_data[ (fieldname, urim) ]["MementoEmbed preferences"], 
                md._data[ (fieldname, urim) ]["MementoEmbed preferences"],
                "failed to match 'MementoEmbed preferences' for ( '{}', '{}')".format(fieldname, urim)
                )

            self.assertEqual(
                expected_data[ (fieldname, urim) ]["Raintale preferences"], 
                md._data[ (fieldname, urim) ]["Raintale preferences"],
                "failed to match 'Raintale preferences' for ( '{}', '{}')".format(fieldname, urim)
                )

            self.assertEqual(
                expected_data[ (fieldname, urim) ]["sanitized field name"], 
                md._data[ (fieldname, urim) ]["sanitized field name"],
                "failed to match 'sanitized field name' for ( '{}', '{}')".format(fieldname, urim)
                )

            self.assertEqual(
                expected_data[ (fieldname, urim) ]["base field name"], 
                md._data[ (fieldname, urim) ]["base field name"],
                "failed to match 'base field name' for ( '{}', '{}')".format(fieldname, urim)
                )

        # TODO: make test for this
        # pp.pprint(md.get_sanitized_template())

        endpoint_data = md.get_endpoints_and_preferences_with_fields()

        for fieldname, urim in expected_data:

            if fieldname != "{{ element.surrogate.urim }}":

                endpoint = expected_data[ (fieldname, urim) ]["full endpoint"]
                me_preferences = expected_data[ (fieldname, urim) ]["MementoEmbed preferences"]

                self.assertIn(
                    (fieldname, urim),
                    endpoint_data[ (endpoint, me_preferences) ]["fields"],
                    msg="Fieldname {} and URI-M {}, not in endpoint data for {} with prefs {}".format(
                        fieldname, urim, endpoint, me_preferences
                    )
                )



if __name__ == '__main__':
    unittest.main()
