import unittest
import os
import pprint
import json

import requests
import requests_mock

from raintale.storytellers.filetemplate import FileTemplateStoryTeller

testdir = os.path.dirname(os.path.realpath(__file__))

class TestFileTemplate(unittest.TestCase):

    def test_generate_story(self):
        
        mementoembed_api = "mock://127.0.0.1:9899/shouldnotwork" # should go nowhere

        adapter = requests_mock.Adapter()
        session = requests.Session()
        session.mount('mock', adapter)

        template_str = """<xml>
<title>{{ title }}</title>
<collection_url>{{ collection_url }}</collection_url>
<generated_by>{{ generated_by }}</generated_by>
{% for element in elements %}
{% if element.type == 'link' %}
<element_title>{{ element.surrogate.title }}</element_title>
<element_snippet>{{ element.surrogate.snippet }}</element_snippet>
<element_urim>{{ element.surrogate.urim }}</element_urim>
<element_archiveuri>{{ element.surrogate.archive_uri }}</element_archiveuri>
{% else %}
<element_text>{{ element.text }}</element_text>
{% endif %}
{% endfor %}
</xml>
        """

        with open("{}/../testinputs/test-story.json".format(testdir)) as f:
            story_data = json.load(f)

        output_filename = "/tmp/raintale_testing.out"

        ftst = FileTemplateStoryTeller(output_filename)

        self.assertEqual(ftst.output_filename, output_filename, "Output filename was not set properly in FileTemplateStoryTeller")

        contentdata_output1 = {
            "urim": "This is a test URI-M for memento #1",
            "generation-time": "2018-07-20T16:27:10Z",
            "title": "This is a test title for memento #1",
            "snippet": "This is a test snippet for memento #1",
            "memento-datetime": "2009-05-22T22:12:51Z"
        }

        contentdata_json1 = json.dumps(contentdata_output1)
        adapter.register_uri(
            'GET', "{}/services/memento/contentdata/{}".format(
                mementoembed_api, story_data["elements"][1]["value"]), text=contentdata_json1)

        contentdata_output2 = {
            "urim": "This is a test URI-M for memento #2",
            "generation-time": "2018-07-20T16:27:10Z",
            "title": "This is a test title for memento #2",
            "snippet": "This is a test snippet for memento #2",
            "memento-datetime": "2009-05-22T22:12:51Z"
        }

        contentdata_json2 = json.dumps(contentdata_output2)
        adapter.register_uri(
            'GET', "{}/services/memento/contentdata/{}".format(
                mementoembed_api, story_data["elements"][3]["value"]), text=contentdata_json2)

        archivedata_output1 = {
            "urim": "This is a test URI-M for memento #1",
            "generation-time": "2019-06-05T19:18:18Z",
            "archive-uri": "This is an archive URI for memento #1",
            "archive-name": "WEBARCHIVE.ORG.UK",
            "archive-favicon": "https://www.webarchive.org.uk/favicon.ico",
            "archive-collection-id": None,
            "archive-collection-name": None,
            "archive-collection-uri": None
        }

        archivedata_json1 = json.dumps(archivedata_output1)
        adapter.register_uri(
            'GET', "{}/services/memento/archivedata/{}".format(
                mementoembed_api, story_data["elements"][1]["value"]), text=archivedata_json1)

        archivedata_output2 = {
            "urim": "This is a test URI-M for memento #2",
            "generation-time": "2019-06-05T19:18:18Z",
            "archive-uri": "This is an archive URI for memento #2",
            "archive-name": "WEBARCHIVE.ORG.UK",
            "archive-favicon": "https://www.webarchive.org.uk/favicon.ico",
            "archive-collection-id": None,
            "archive-collection-name": None,
            "archive-collection-uri": None
        }

        archivedata_json2 = json.dumps(archivedata_output2)
        adapter.register_uri(
            'GET', "{}/services/memento/archivedata/{}".format(
                mementoembed_api, story_data["elements"][3]["value"]), text=archivedata_json2)

        expected_output = """<xml>
<title>{}</title>
<collection_url>{}</collection_url>
<generated_by>{}</generated_by>


<element_text>{}</element_text>



<element_title>{}</element_title>
<element_snippet>{}</element_snippet>
<element_urim>{}</element_urim>
<element_archiveuri>{}</element_archiveuri>



<element_text>{}</element_text>



<element_title>{}</element_title>
<element_snippet>{}</element_snippet>
<element_urim>{}</element_urim>
<element_archiveuri>{}</element_archiveuri>


</xml>
        """.format(
            story_data["title"],
            story_data["collection_url"],
            story_data["generated_by"],
            story_data["elements"][0]["value"],
            "This is a test title for memento #1",
            "This is a test snippet for memento #1",
            story_data["elements"][1]["value"],
            "This is an archive URI for memento #1",
            story_data["elements"][2]["value"],
            "This is a test title for memento #2",
            "This is a test snippet for memento #2",            
            story_data["elements"][3]["value"],
            "This is an archive URI for memento #2"
        )

        self.maxDiff = None

        actual_output = ftst.generate_story(story_data, mementoembed_api, template_str, session=session)

        self.assertEqual(expected_output, actual_output)

######### NEXT TEST FOLLOWS ######## LINE HERE FOR LEGIBILITY ######

    def test_generate_story_with_preferences_and_filters(self):
        
        mementoembed_api = "mock://127.0.0.1:9899/shouldnotwork" # should go nowhere

        adapter = requests_mock.Adapter()
        session = requests.Session()
        session.mount('mock', adapter)

        template_str = """<xml>
<title>{{ title|reverse|upper }}</title>
<collection_url>{{ collection_url }}</collection_url>
<generated_by>{{ generated_by }}</generated_by>
{% for element in elements %}
{% if element.type == 'link' %}
<element_title>{{ element.surrogate.title|reverse|upper }}</element_title>
<element_snippet>{{ element.surrogate.snippet|upper }}</element_snippet>
<element_urim>{{ element.surrogate.urim }}</element_urim>
<element_archiveuri>{{ element.surrogate.archive_uri }}</element_archiveuri>
<element_memento_datetime>{{ element.surrogate.memento_datetime.strftime('%y-%m-%d') }}</element_memento_datetime>
{% else %}
<element_text>{{ element.text }}</element_text>
{% endif %}
{% endfor %}
</xml>
        """

        with open("{}/../testinputs/test-story.json".format(testdir)) as f:
            story_data = json.load(f)

        output_filename = "/tmp/raintale_testing.out"

        ftst = FileTemplateStoryTeller(output_filename)

        self.assertEqual(ftst.output_filename, output_filename, "Output filename was not set properly in FileTemplateStoryTeller")

        contentdata_output1 = {
            "urim": "This is a test URI-M for memento #1",
            "generation-time": "2018-07-20T16:27:10Z",
            "title": "This is a test title for memento #1",
            "snippet": "This is a test snippet for memento #1",
            "memento-datetime": "2009-05-22T22:12:51Z"
        }

        contentdata_json1 = json.dumps(contentdata_output1)
        adapter.register_uri(
            'GET', "{}/services/memento/contentdata/{}".format(
                mementoembed_api, story_data["elements"][1]["value"]), text=contentdata_json1)

        contentdata_output2 = {
            "urim": "This is a test URI-M for memento #2",
            "generation-time": "2018-07-20T16:27:10Z",
            "title": "This is a test title for memento #2",
            "snippet": "This is a test snippet for memento #2",
            "memento-datetime": "2009-05-22T22:12:51Z"
        }

        contentdata_json2 = json.dumps(contentdata_output2)
        adapter.register_uri(
            'GET', "{}/services/memento/contentdata/{}".format(
                mementoembed_api, story_data["elements"][3]["value"]), text=contentdata_json2)

        archivedata_output1 = {
            "urim": "This is a test URI-M for memento #1",
            "generation-time": "2019-06-05T19:18:18Z",
            "archive-uri": "This is an archive URI for memento #1",
            "archive-name": "WEBARCHIVE.ORG.UK",
            "archive-favicon": "https://www.webarchive.org.uk/favicon.ico",
            "archive-collection-id": None,
            "archive-collection-name": None,
            "archive-collection-uri": None
        }

        archivedata_json1 = json.dumps(archivedata_output1)
        adapter.register_uri(
            'GET', "{}/services/memento/archivedata/{}".format(
                mementoembed_api, story_data["elements"][1]["value"]), text=archivedata_json1)

        archivedata_output2 = {
            "urim": "This is a test URI-M for memento #2",
            "generation-time": "2019-06-05T19:18:18Z",
            "archive-uri": "This is an archive URI for memento #2",
            "archive-name": "WEBARCHIVE.ORG.UK",
            "archive-favicon": "https://www.webarchive.org.uk/favicon.ico",
            "archive-collection-id": None,
            "archive-collection-name": None,
            "archive-collection-uri": None
        }

        archivedata_json2 = json.dumps(archivedata_output2)
        adapter.register_uri(
            'GET', "{}/services/memento/archivedata/{}".format(
                mementoembed_api, story_data["elements"][3]["value"]), text=archivedata_json2)

        expected_output = """<xml>
<title>{}</title>
<collection_url>{}</collection_url>
<generated_by>{}</generated_by>


<element_text>{}</element_text>



<element_title>{}</element_title>
<element_snippet>{}</element_snippet>
<element_urim>{}</element_urim>
<element_archiveuri>{}</element_archiveuri>
<element_memento_datetime>{}</element_memento_datetime>



<element_text>{}</element_text>



<element_title>{}</element_title>
<element_snippet>{}</element_snippet>
<element_urim>{}</element_urim>
<element_archiveuri>{}</element_archiveuri>
<element_memento_datetime>{}</element_memento_datetime>


</xml>
        """.format(
            story_data["title"][::-1].upper(),
            story_data["collection_url"],
            story_data["generated_by"],
            story_data["elements"][0]["value"],
            "This is a test title for memento #1"[::-1].upper(),
            "This is a test snippet for memento #1".upper(),
            story_data["elements"][1]["value"],
            "This is an archive URI for memento #1",
            "09-05-22",
            story_data["elements"][2]["value"],
            "This is a test title for memento #2"[::-1].upper(),
            "This is a test snippet for memento #2".upper(),            
            story_data["elements"][3]["value"],
            "This is an archive URI for memento #2",
            "09-05-22"
        )

        self.maxDiff = None

        actual_output = ftst.generate_story(story_data, mementoembed_api, template_str, session=session)

        self.assertEqual(expected_output, actual_output)

if __name__ == '__main__':
    unittest.main()
