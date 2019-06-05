import logging
import pprint

from .storyteller import FileStoryteller

class VideoStoryTeller(FileStoryteller):

    def generate_story(self, story_data, mementoembed_api, story_template):

        story_output_data = {
            "title": story_data['title'],
            "generated_by": story_data['generated_by'],
            "collection_url": story_data['collection_url'],
            "elements": []
        }

        scored_sentences = {}
        scored_images = {}

        for element in story_elements:

            try:

                if element['type'] == 'link':

                    # request sentences from sentence ranking service, normalize scores for para and sentence

                    # request images from imagedara service

                    # story_output_data["elements"].append(
                    #     "text": None,
                    #     "image": None
                    # )
                
                elif element['type'] == 'text':

                    # give this text a really high score

                    # story_output_data["elements"].append(
                    #     {
                    #         "text": element['value']
                    #     }
                    # )

                else:
                    module_logger.warning(
                        "element of type {} is unsupported, skipping...".format(element['type'])
                    )

            except KeyError:

                module_logger.exception(
                    "cannot process story element data of {}, skipping".format(element)
                )


        module_logger.debug(
            "story_output_data: {}".format(pprint.pformat(story_output_data))
        )

        return story_output_data


    def publish_story(self, story_output_data):
        pass


