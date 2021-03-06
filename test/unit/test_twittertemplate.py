import unittest
import os
import pprint
import json

import requests
import requests_mock

from raintale.storytellers.twitter import TwitterStoryTeller

testdir = os.path.dirname(os.path.realpath(__file__))

class TestFileTemplate(unittest.TestCase):

    def test_generate_story(self):
        
        mementoembed_api = "mock://127.0.0.1:9899/shouldnotwork" # should go nowhere

        adapter = requests_mock.Adapter()
        session = requests.Session()
        session.mount('mock', adapter)

        template_str = """{# RAINTALE MULTIPART TEMPLATE #}
{# RAINTALE TITLE PART #}
{{ title }}

{% if generated_by is not none %}Story By: {{ generated_by }}{% endif %}

{% if collection_url is not none %}{{ collection_url }}{% endif %}
{# RAINTALE ELEMENT PART #}

{{ element.surrogate.title }}

{{ element.surrogate.memento_datetime }}

{{ element.surrogate.urim }}

{# RAINTALE ELEMENT MEDIA #}
"""

        with open("{}/../testinputs/test-story.json".format(testdir)) as f:
            story_data = json.load(f)

        credentials_filename = "/tmp/credentials.yaml"

        with open(credentials_filename, 'w') as f:
            f.write("""consumer_key: XXX
consumer_secret: XXX
access_token_key: XXX
access_token_secret: XXX""")

        tst = TwitterStoryTeller(credentials_filename, auth_check=False)

        self.assertEqual(tst.credentials_filename, credentials_filename, "Output filename was not set properly in FileTemplateStoryTeller")

        contentdata_output1 = {
            "urim": "This is a test URI-M for memento #1",
            "generation-time": "2018-07-20T16:27:10Z",
            "title": "This is a test title for memento #1",
            "snippet": "This is a test snippet for memento #1",
            "memento-datetime": "2010-04-24T00:00:01Z"
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
            "memento-datetime": "2010-04-24T00:00:02Z"
        }

        contentdata_json2 = json.dumps(contentdata_output2)
        adapter.register_uri(
            'GET', "{}/services/memento/contentdata/{}".format(
                mementoembed_api, story_data["elements"][3]["value"]), text=contentdata_json2)

        expected_output = {
            "main_post": "My Story Title\n\nStory By: Generated By\n\nhttps://archive.example.com/mycollection",
            "comment_posts": [
                {
                    "text": story_data["elements"][0]["value"],
                    "media": []
                },
                {
                    "text": "\nThis is a test title for memento #1\n\n2010-04-24 00:00:01\n\n{}\n".format(
                        story_data["elements"][1]["value"]),
                    "media": []
                },
                {
                    "text": story_data["elements"][2]["value"],
                    "media": []
                },
                {
                    "text": "\nThis is a test title for memento #2\n\n2010-04-24 00:00:02\n\n{}\n".format(
                        story_data["elements"][3]["value"]),
                    "media": []
                }
            ]
        }

        # pp = pprint.PrettyPrinter(indent=4)

        # print("expected:")
        # pp.pprint(expected_output)

        # print("actual:")
        # pp.pprint(tst.generate_story(story_data, mementoembed_api, template_str, session=session))

        self.maxDiff = None
        self.assertEqual(expected_output, tst.generate_story(story_data, mementoembed_api, template_str, session=session))

    def test_generate_story_with_images(self):
        
        mementoembed_api = "mock://127.0.0.1:9899/shouldnotwork" # should go nowhere

        adapter = requests_mock.Adapter()
        session = requests.Session()
        session.mount('mock', adapter)

        template_str = """{# RAINTALE MULTIPART TEMPLATE #}
{# RAINTALE TITLE PART #}
{{ title }}

{% if generated_by is not none %}Story By: {{ generated_by }}{% endif %}

{% if collection_url is not none %}{{ collection_url }}{% endif %}
{# RAINTALE ELEMENT PART #}

{{ element.surrogate.title }}

{{ element.surrogate.memento_datetime }}

{{ element.surrogate.urim }}

{# RAINTALE ELEMENT MEDIA #}
{{ element.surrogate.thumbnail|prefer thumbnail_width=1024,remove_banner=yes }}
{{ element.surrogate.image|prefer rank=1 }}
{{ element.surrogate.image|prefer rank=2 }}
{{ element.surrogate.image|prefer rank=3 }}
"""

        with open("{}/../testinputs/test-story.json".format(testdir)) as f:
            story_data = json.load(f)

        credentials_filename = "/tmp/credentials.yaml"

        with open(credentials_filename, 'w') as f:
            f.write("""consumer_key: XXX
consumer_secret: XXX
access_token_key: XXX
access_token_secret: XXX""")

        tst = TwitterStoryTeller(credentials_filename, auth_check=False)

        self.assertEqual(tst.credentials_filename, credentials_filename, "Output filename was not set properly in FileTemplateStoryTeller")

        contentdata_output1 = {
            "urim": "This is a test URI-M for memento #1",
            "generation-time": "2018-07-20T16:27:10Z",
            "title": "This is a test title for memento #1",
            "snippet": "This is a test snippet for memento #1",
            "memento-datetime": "2010-04-24T00:00:01Z"
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
            "memento-datetime": "2010-04-24T00:00:02Z"
        }

        contentdata_json2 = json.dumps(contentdata_output2)
        adapter.register_uri(
            'GET', "{}/services/memento/contentdata/{}".format(
                mementoembed_api, story_data["elements"][3]["value"]), text=contentdata_json2)

        imagedata_output1 = {
            "urim": "https://www.webarchive.org.uk/wayback/archive/20090522221251/http://blasttheory.co.uk/",
            "processed urim": "https://www.webarchive.org.uk/wayback/archive/20090522221251im_/http://blasttheory.co.uk/",
            "generation-time": "2019-05-30T03:19:08Z",
            "ranked images": [
                "memento #1 image rank 1",
                "memento #1 image rank 2",
                "memento #1 image rank 3"
            ]
        }

        imagedata_json1 = json.dumps(imagedata_output1)
        adapter.register_uri(
            'GET', "{}/services/memento/imagedata/{}".format(
                mementoembed_api, story_data["elements"][1]["value"]), text=imagedata_json1)

        imagedata_output2 = {
            "urim": "https://www.webarchive.org.uk/wayback/archive/20090522221251/http://blasttheory.co.uk/",
            "processed urim": "https://www.webarchive.org.uk/wayback/archive/20090522221251im_/http://blasttheory.co.uk/",
            "generation-time": "2019-05-30T03:19:08Z",
            "ranked images": [
                "memento #2 image rank 1",
                "memento #2 image rank 2",
                "memento #2 image rank 3"
            ]
        }

        imagedata_json2 = json.dumps(imagedata_output2)
        adapter.register_uri(
            'GET', "{}/services/memento/imagedata/{}".format(
                mementoembed_api, story_data["elements"][3]["value"]), text=imagedata_json2)

        thumbnail_output1 = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x01\x03\x00\x00\x00%\xdbV\xca\x00\x00\x00\x06PLTE\x00\x00\x00\xff\xff\xff\xa5\xd9\x9f\xdd\x00\x00\x00\tpHYs\x00\x00\x0e\xc4\x00\x00\x0e\xc4\x01\x95+\x0e\x1b\x00\x00\x00\nIDAT\x08\x99c`\x00\x00\x00\x02\x00\x01\xf4qd\xa6\x00\x00\x00\x00IEND\xaeB`\x82'

        adapter.register_uri(
            'GET', "{}/services/product/thumbnail/{}".format(
                mementoembed_api, story_data["elements"][1]["value"]), content=thumbnail_output1)

        thumbnail_output2 = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x01\x03\x00\x00\x00%\xdbV\xca\x00\x00\x00\x06PLTE\xff\xff\xff\xff\xff\xffU|\xf5l\x00\x00\x00\tpHYs\x00\x00\x0e\xc4\x00\x00\x0e\xc4\x01\x95+\x0e\x1b\x00\x00\x00\nIDAT\x08\x99c`\x00\x00\x00\x02\x00\x01\xf4qd\xa6\x00\x00\x00\x00IEND\xaeB`\x82'

        adapter.register_uri(
            'GET', "{}/services/product/thumbnail/{}".format(
                mementoembed_api, story_data["elements"][3]["value"]), content=thumbnail_output2)

        expected_output = {
            "main_post": "My Story Title\n\nStory By: Generated By\n\nhttps://archive.example.com/mycollection",
            "comment_posts": [
                {
                    "text": story_data["elements"][0]["value"],
                    "media": []
                },
                {
                    "text": "\nThis is a test title for memento #1\n\n2010-04-24 00:00:01\n\n{}\n".format(
                        story_data["elements"][1]["value"]),
                    "media": [
                        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQMAAAAl21bKAAAABlBMVEUAAAD///+l2Z/dAAAACXBI\nWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNgAAAAAgAB9HFkpgAAAABJRU5ErkJggg==\n",
                        "memento #1 image rank 1",
                        "memento #1 image rank 2",
                        "memento #1 image rank 3"
                    ]
                },
                {
                    "text": story_data["elements"][2]["value"],
                    "media": []
                },
                {
                    "text": "\nThis is a test title for memento #2\n\n2010-04-24 00:00:02\n\n{}\n".format(
                        story_data["elements"][3]["value"]),
                    "media": [
                        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQMAAAAl21bKAAAABlBMVEX///////9VfPVsAAAACXBI\nWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNgAAAAAgAB9HFkpgAAAABJRU5ErkJggg==\n",
                        "memento #2 image rank 1",
                        "memento #2 image rank 2",
                        "memento #2 image rank 3"
                    ]
                }
            ]
        }

        # pp = pprint.PrettyPrinter(indent=4)

        # print("expected:")
        # pp.pprint(expected_output)

        # print("actual:")
        # pp.pprint(tst.generate_story(story_data, mementoembed_api, template_str, session=session))

        self.maxDiff = None
        self.assertEqual(expected_output, tst.generate_story(story_data, mementoembed_api, template_str, session=session))


if __name__ == '__main__':
    unittest.main()
