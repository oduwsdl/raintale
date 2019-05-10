import logging
import mimetypes
import tempfile
import os
import time

import facebook

from jinja2 import Template

from .storyteller import ServiceStoryteller, get_story_elements, StoryTellerCredentialParseError, split_multipart_template
from ..surrogatedata import get_memento_data, get_template_surrogate_fields, datauri_to_data

module_logger = logging.getLogger('raintale.storytellers.facebook')

class FacebookStoryTeller(ServiceStoryteller):

    description = "(EXPERIMENTAL) Given input data and a template file, this storyteller publishes a story as a Facebook thread."

    def load_credentials_filename(self):

        super(FacebookStoryTeller, self).load_credentials_filename()

        expected_credentials = [
            'page_id',
            'access_token'
        ]

        for key in expected_credentials:
            if key not in self.credentials:
                msg = "Credential file is missing the field {}, cannot continue...".format(key)
                module_logger.critical(msg)

                raise StoryTellerCredentialParseError(msg)

    def auth(self):

        self.graph = facebook.GraphAPI(
            access_token=self.credentials['access_token'],
            version="2.12"
        )

    def generate_story(self, story_data, mementoembed_api, story_template):

        title_template, element_template, media_template_list = split_multipart_template(story_template)

        story_elements = get_story_elements(story_data)

        module_logger.debug("media_template_list: {}".format(media_template_list))
        
        story_output_data = {
            "main_post": "",
            "comment_posts": []
        }

        story_output_data["main_post"] = Template(title_template).render(
                title=story_data['title'],
                generated_by=story_data['generated_by'],
                collection_url=story_data['collection_url']
        )

        template_surrogate_fields = get_template_surrogate_fields(element_template)

        template_media_fields = []
        
        for field in media_template_list:

            # there should only be one
            template_media_fields.append(
                get_template_surrogate_fields(field)[0]
            )

        module_logger.debug("template_media_fields: {}".format(template_media_fields))

        module_logger.info("preparing to iterate through {} story "
            "elements".format(len(story_elements)))

        for element in story_elements:

            try:

                if element['type'] == 'link':

                    urim = element['value']

                    memento_data = get_memento_data(
                        template_surrogate_fields, 
                        mementoembed_api, 
                        urim)

                    module_logger.debug("memento_data: {}".format(memento_data))

                    media_uris = []

                    module_logger.debug("template_media_fields: {}".format(template_media_fields))

                    for field in template_media_fields:

                        module_logger.debug("field: {}".format(field))
                        field_data = get_memento_data(
                            [field],
                            mementoembed_api,
                            urim
                        )
                        media_uris.append(
                                Template(field).render(
                                surrogate=field_data
                        ))

                    module_logger.debug("media_uris: {}".format(media_uris))

                    story_output_data["comment_posts"].append(
                        {
                            "text": Template(element_template).render(
                                surrogate=memento_data
                            ),
                            "media": media_uris
                        }
                    )

                else:
                    module_logger.warning(
                        "element of type {} is unsupported, skipping...".format(element['type'])
                    )

            except KeyError:

                module_logger.exception(
                    "cannot process story element data of {}, skipping".format(element)
                )

        return story_output_data

    def publish_story(self, story_output_data):

        page_id = self.credentials['page_id']

        module_logger.info("publishing story as a thread to Facebook page {}".format(page_id))

        title_post = self.graph.put_object(
            parent_object=page_id,
            connection_name="feed",
            message=story_output_data["main_post"]
        )

        commentcounter = 0
        commentcount = len(story_output_data["comment_posts"])

        for thread_post in story_output_data["comment_posts"]:

            commentcounter += 1
            module_logger.info("publishing story element {} of {}".format(commentcounter, commentcount))

            element_post = self.graph.put_object(
                parent_object=title_post['id'], connection_name="comments",
                message=thread_post["text"]
            )

            module_logger.info("sleeping for 2 seconds for Facebook's benefit...")
            time.sleep(2)

        module_logger.info(
            "Your story has been told on Facebook. Find it at "
            "https://www.facebook.com/permalink.php?story_fbid={}&id={}".format(
                title_post['id'].split('_')[1], page_id
            )
        )

