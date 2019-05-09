import logging

from yaml import load, Loader

module_logger = logging.getLogger('raintale.storytellers.storyteller')

class StoryTellerException(Exception):
    pass

class StoryTellerCredentialParseError(StoryTellerException):
    pass

class StoryTellerStoryParseError(StoryTellerException):
    pass

class StoryTellerMultipartTemplateParseError(StoryTellerException):
    pass

def get_story_elements(story_data):

    try:
        story_elements = story_data['elements']
        return story_elements
    except KeyError:
        msg = "Cannot tell story. Story does not contain elements. "
        module_logger.exception(msg)
        raise StoryTellerStoryParseError(msg)

def split_multipart_template(template_contents):

    if template_contents[0:34] != '{# RAINTALE MULTIPART TEMPLATE #}\n':
        msg = "Multipart Template required, but not submitted, cannot continue..."
        module_logger.critical(msg)
        raise StoryTellerMultipartTemplateParseError(msg)

    template_contents = template_contents[34:]

    if template_contents[0:26] != '{# RAINTALE TITLE PART #}\n':
        msg = "Raintale Title Part required in Multipart Template, but not present, cannot continue..."
        module_logger.critical(msg)
        raise StoryTellerMultipartTemplateParseError(msg)

    template_contents = template_contents[26:]

    try:
        title_template, element_template = template_contents.split('{# RAINTALE ELEMENT PART #}\n')
    except ValueError:
        msg = "Raintale Element Part required in Multipart Template, but not present, cannot continue..."
        module_logger.critical(msg)
        raise StoryTellerMultipartTemplateParseError(msg)

    try:
        element_template, media_template = element_template.split('{# RAINTALE ELEMENT MEDIA #}')
        media_list = media_template.split('\n')
        
        # TODO: this should not be necessary
        cleaned_media_list = []
        module_logger.debug("media_list: {}".format(media_list))

        for item in media_list:

            if item != '':
                cleaned_media_list.append(item)

        module_logger.debug("cleaned_media_list: {}".format(cleaned_media_list))

    except ValueError:
        media_list = []

    return title_template, element_template, cleaned_media_list

class Storyteller:

    description = "ERROR"

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

    def __init__(self, credentials_filename):
        self.credentials_filename = credentials_filename
        self.load_credentials_filename()
        self.auth()

    def load_credentials_filename(self):

        with open(self.credentials_filename) as f:
            self.credentials = load(f, Loader=Loader)

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


