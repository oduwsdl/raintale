import logging

module_logger = logging.getLogger('raintale.storytellers')

class StoryTellerException(Exception):
    pass

class StoryTellerCredentialParseError(StoryTellerException):
    pass

class StoryTellerStoryParseError(StoryTellerException):
    pass

class StoryTeller:
    def __init__(self, storygenerator, story_data, credentials):

        self.storygenerator = storygenerator
        self.story_data = story_data
        self.credentials = credentials

    def tell_story(self):
        raise NotImplementedError(
            "StoryTeller class is not meant to be called directly. "
            "Create a child class to use StoryTeller functionality.")

class RawHTMLStoryTeller(StoryTeller):
    
    def tell_story(self):

        module_logger.debug("telling story using RawHTMLStoryTeller")
        
        story_output = ""

        try:
            output_filename = self.credentials['output_filename']
        except KeyError:
            msg = "Credentials do not contain output filename for " \
                "raw HTML story output"

            module_logger.exception(msg)

            raise StoryTellerCredentialParseError(msg)

        try:
            story_elements = self.story_data['elements']
        except KeyError:
            msg = "Cannot tell story. Story does not contain elements. "
            module_logger.exception(msg)
            raise StoryTellerStoryParseError(msg)

        module_logger.info("preparing to iterate through {} story "
            "elements".format(len(story_elements)))

        for element in story_elements:

            module_logger.debug("examining story element {}".format(element))

            try:

                if element['type'] == 'link':

                    raw_element_html = \
                        self.storygenerator.get_urielement_rawhtml(
                            element['value'])

                    story_output += "<p>\n{}\n</p>\n".format(raw_element_html)

                else:
                    module_logger.warn(
                        "skipping unsupported story element type of {}".format(
                            element['type']
                        ))

            except KeyError:

                module_logger.error(
                    "cannot process story element data of {}, skipping".format(element)
                )

        with open(output_filename, 'w') as f:
            f.write(story_output)

storytellers = {
    "rawhtml": RawHTMLStoryTeller
}
