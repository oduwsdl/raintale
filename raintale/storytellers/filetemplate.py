import logging
import pprint

from jinja2 import Environment

from .storyteller import FileStoryteller, get_story_elements
from ..surrogatedata import MementoData

module_logger = logging.getLogger('raintale.storytellers.filetemplate')

class FileTemplateStoryTellerTemplateUnsupportedElement(Exception):
    
    def __init__(self, message):
        self.message = message

class WrongTemplateTypeError(Exception):
    
    def __init__(self, message):
        self.message = message

class FileTemplateStoryTeller(FileStoryteller):
    
    description = "Given input data and a template file, this storyteller generates a story formatted based on the template and saves it to an output file."

    def generate_story(self, story_data, mementoembed_api, story_template, session=None):
        
        if template_contents[0:34] == '{# RAINTALE MULTIPART TEMPLATE #}\n':
            msg = "Multipart Template submitted but this type of story requires a simple template, cannot continue..."
            module_logger.critical(msg)
            raise WrongTemplateTypeError(msg)

        story_elements = get_story_elements(story_data)

        elements = []

        module_logger.info("preparing to iterate through {} story "
            "elements".format(len(story_elements)))

        elementcounter = 1
        md = MementoData(story_template, mementoembed_api)

        for element in story_elements:

            if element['type'] == 'link':

                urim = element['value']
                md.add(urim)

        for element in story_elements:

            module_logger.info("processing element {} of {}".format(
                elementcounter, len(story_elements))
            )

            module_logger.debug("examining story element {}".format(element))

            try:

                if element['type'] == 'link':

                    module_logger.info("encountered a story link element")

                    urim = element['value']
                    link_data = {}

                    memento_data = md.get_memento_data(urim, session=session)

                    module_logger.debug("memento_data: {}".format(memento_data))

                    link_data['type'] = 'link'
                    link_data['surrogate'] = memento_data

                    elements.append(link_data)

                elif element['type'] == 'text':

                    module_logger.info("encountered a story text element")

                    text = element['value']

                    elements.append(
                        {
                            "type": "text",
                            "text": text
                        }
                    )

                else:
                    module_logger.warning(
                        "element of type {} is unsupported, skipping...".format(element['type'])
                    )

            except KeyError:

                module_logger.exception(
                    "cannot process story element data of {}, skipping...".format(element)
                )

            elementcounter += 1

        module_logger.debug("elements: {}".format(
            pprint.pformat(elements)
        ))

        if 'metadata' in story_data:
            metadata = story_data['metadata']
        else:
            metadata = None

        sanitized_template = md.get_sanitized_template()

        module_logger.debug("sanitized template:\n\n {}\n\n".format(sanitized_template))

        env = Environment()
        template = env.from_string(sanitized_template)
        rendered_story = template.render(
            title=story_data['title'],
            generated_by=story_data['generated_by'],
            collection_url=story_data['collection_url'],
            story_image=story_data['story image'],
            generation_date=story_data['generation_date'],
            metadata=metadata,
            elements=elements
        )

        return rendered_story

    def publish_story(self, story_output_data):

        module_logger.info("writing story to file named {}".format(self.output_filename))

        with open(self.output_filename, 'w') as f:
            f.write(story_output_data)

        module_logger.info(
            "Your story has been told to file {}".format(
                self.output_filename
            )
        )

        return self.output_filename
