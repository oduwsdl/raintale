import logging

from jinja2 import Template

from .storyteller import FileStoryteller, get_story_elements
from ..surrogatedata import get_memento_data, get_template_surrogate_fields

module_logger = logging.getLogger('raintale.storytellers.filetemplate')

class FileTemplateStoryTeller(FileStoryteller):
    
    description = "Given input data and a template file, this storyteller generates a story formatted based on the template."

    def generate_story(self, story_data, mementoembed_api, story_template):

        story_elements = get_story_elements(story_data)

        surrogates = []

        module_logger.info("preparing to iterate through {} story "
            "elements".format(len(story_elements)))

        elementcounter = 1

        template_surrogate_fields = get_template_surrogate_fields(story_template)

        for element in story_elements:

            module_logger.info("processing element {} of {}".format(
                elementcounter, len(story_elements))
            )

            module_logger.debug("examining story element {}".format(element))

            try:

                if element['type'] == 'link':

                    urim = element['value']

                    memento_data = get_memento_data(
                        template_surrogate_fields, 
                        mementoembed_api, 
                        urim)

                    surrogates.append(memento_data)

                else:
                    module_logger.warning(
                        "element of type {} is unsupported, skipping...".format(element['type'])
                    )

            except KeyError as e:

                module_logger.exception(
                    "cannot process story element data of {}, skipping".format(element)
                )

                raise e

            elementcounter += 1

        return Template(story_template).render(
                title=story_data['title'],
                generated_by=story_data['generated_by'],
                collection_url=story_data['collection_url'],
                surrogates=surrogates
            )

    def publish_story(self, story_output_data):

        module_logger.info("writing story to file named {}".format(self.output_filename))

        with open(self.output_filename, 'w') as f:
            f.write(story_output_data)

        module_logger.info(
            "Your story has been told to file {}".format(
                self.output_filename
            )
        )
