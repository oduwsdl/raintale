import logging
import mimetypes
import tempfile
import os
import time
import sys # for debugging

import facebook

from jinja2 import Template

from .storyteller import ServiceStoryteller, get_story_elements, StoryTellerCredentialParseError, split_multipart_template

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

