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
            <element0>{{ title }}</element0>
            <element1>{{ collection_url }}</element1>
            <element2>{{ generated_by }}</element2>{% for element in elements %}{% if element.type == 'link' %}<elementi>{{ element.surrogate.title }}</elementi>
            <elementj>{{ element.surrogate.snippet }}</elementj>
            <elementk>{{ element.surrogate.urim }}</elementk>
            <elementl>{{ element.surrogate.archive_uri }}</elementl>{% else %}<elementm>{{ element.text }}</elementm>{% endif %}{% endfor %}
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
            <element0>{}</element0>
            <element1>{}</element1>
            <element2>{}</element2><elementm>{}</elementm><elementi>{}</elementi>
            <elementj>{}</elementj>
            <elementk>{}</elementk>
            <elementl>{}</elementl><elementm>{}</elementm><elementi>{}</elementi>
            <elementj>{}</elementj>
            <elementk>{}</elementk>
            <elementl>{}</elementl>
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
        self.assertEqual(expected_output, ftst.generate_story(story_data, mementoembed_api, template_str, session=session))

if __name__ == '__main__':
    unittest.main()
