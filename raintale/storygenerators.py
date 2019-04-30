import requests
import logging

module_logger = logging.getLogger('raintale.storygenerators')

class StoryGenerator:

    def __init__(self, mementoembed_api):

        self.mementoembed_api = mementoembed_api

        if mementoembed_api.endswith('/'):
            self.mementoembed_api = mementoembed_api[:-1]

    def get_urielement_rawhtml(self, urim):
        raise NotImplementedError(
            "StoryGenerator class is not meant to be called directly. "
            "Create a child class to use StoryGenerator functionality.")

    def get_urielement_data(self, urim):
        raise NotImplementedError(
            "StoryGenerator class is not meant to be called directly. "
            "Create a child class to use StoryGenerator functionality.")

class RawHTMLSocialcardGenerator(StoryGenerator):

    def get_urielement_rawhtml(self, urim):
        
        element_data = ""

        api_endpoint = "{}/services/product/socialcard/{}".format(
            self.mementoembed_api, urim
        )

        headers = {
            "Prefer": "using_remote_javascript=no"
        }

        r = requests.get(api_endpoint, headers=headers)

        if r.status_code == 200:
            element_data = r.text
        else:
            # element_data = r.text
            # TODO: raise exception for failed response
            pass
                    
        return element_data        

class ComponentSocialcardGenerator(StoryGenerator):

    def get_urielement_data(self, urim):
        
        element_data = {
            "title": None,
            "text": None,
            "image": None,
            "memento-datetime": None,
            "original-uri": None,
            "archive": None,
            "raw_surrogate": None,
            "errordata": None
        }

        module_logger.debug("calling MementoEmbed contentdata endpoint for URI-M {}".format(urim))

        api_endpoint = "{}/services/memento/contentdata/{}".format(
            self.mementoembed_api, urim
        )

        r = requests.get(api_endpoint)

        if r.status_code == 200:
            element_data["title"] = r.json()["title"]
            element_data["text"] = r.json()["snippet"]
            element_data["memento-datetime"] = r.json()["memento-datetime"]
        else:
            element_data["errordata"] = r.text

        module_logger.debug("calling MementoEmbed bestimage endpoint for URI-M {}".format(urim))

        api_endpoint = "{}/services/memento/bestimage/{}".format(
            self.mementoembed_api, urim
        )

        r = requests.get(api_endpoint)

        if r.status_code == 200:
            element_data["image"] = r.json()["best-image-uri"]
        else:
            element_data["errordata"] = r.text

        module_logger.debug("calling MementoEmbed archivedata endpoint for URI-M {}".format(urim))

        api_endpoint = "{}/services/memento/archivedata/{}".format(
            self.mementoembed_api, urim
        )

        r = requests.get(api_endpoint)
        
        if r.status_code == 200:
            element_data["archive"] = r.json()["archive-name"]
        else:
            element_data["errordata"] = r.text

        api_endpoint = "{}/services/memento/originalresourcedata/{}".format(
            self.mementoembed_api, urim
        )

        r = requests.get(api_endpoint)

        if r.status_code == 200:
            element_data["original-uri"] = r.json()["original-uri"]
        else:
            element_data["errordata"] = r.text
        
        return element_data

storygenerators = {
    "rawhtml_socialcard": RawHTMLSocialcardGenerator,
    "socialcard": ComponentSocialcardGenerator
}
