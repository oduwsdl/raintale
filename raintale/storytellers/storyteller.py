import logging

module_logger = logging.getLogger('raintale.storytellers.storyteller')

class StoryTellerException(Exception):
    pass

class StoryTellerCredentialParseError(StoryTellerException):
    pass

class StoryTellerStoryParseError(StoryTellerException):
    pass

def get_story_elements(story_data):

    try:
        story_elements = story_data['elements']
        return story_elements
    except KeyError:
        msg = "Cannot tell story. Story does not contain elements. "
        module_logger.exception(msg)
        raise StoryTellerStoryParseError(msg)

class Storyteller:

    description = "ERROR"

    @staticmethod
    def test_template_format(story_template):
        raise NotImplementedError(
            "StoryTeller class is not meant to be called directly. "
            "Create a child class to use StoryTeller functionality.")

    def generate_story(self, story_data, mementoembed_api, story_template):
        raise NotImplementedError(
            "StoryTeller class is not meant to be called directly. "
            "Create a child class to use StoryTeller functionality.")

    def publish_story(self, story_output_data):
        raise NotImplementedError(
            "StoryTeller class is not meant to be called directly. "
            "Create a child class to use StoryTeller functionality.")

    def tell_story(self, story_data, mementoembed_api, story_template):

        story_output_data = self.generate_story(story_data, mementoembed_api, story_template)
        self.publish_story(story_output_data)

class ServiceStoryteller(Storyteller):

    requires_file = False
    requires_credentials = True

    def __init__(self, credentials):
        self.credentials = credentials
        self.auth()

    @staticmethod
    def get_required_credentials():
        raise NotImplementedError(
            "ServiceStoryTeller class is not meant to be called directly. "
            "Create a child class to use ServiceStoryTeller functionality.")

    def auth(self):
        raise NotImplementedError(
            "ServiceStoryTeller class is not meant to be called directly. "
            "Create a child class to use ServiceStoryTeller functionality.")

    def reset_credentials(self, credentials):
        raise NotImplementedError(
            "ServiceStoryTeller class is not meant to be called directly. "
            "Create a child class to use ServiceStoryTeller functionality.")


class FileStoryteller(Storyteller):

    requires_file = True
    requires_credentials = False

    def __init__(self, output_filename):
        self.output_filename = output_filename
        module_logger.info("output filename set to {}".format(self.output_filename))

    def reset_output_filename(self, output_filename):
        self.output_filename = output_filename


