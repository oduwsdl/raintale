import logging
import mimetypes
import tempfile
import os
import time
import sys # for debugging
import pprint # for debugging

import twitter

from jinja2 import Template

from .storyteller import ServiceStoryteller, get_story_elements, StoryTellerCredentialParseError, split_multipart_template
from ..surrogatedata import datauri_to_data

module_logger = logging.getLogger('raintale.storytellers.twitter')

class TwitterStoryTeller(ServiceStoryteller):

    description = "Given input data and a template file, this storyteller publishes a story as a Twitter thread."

    def load_credentials_filename(self):

        super(TwitterStoryTeller, self).load_credentials_filename()

        expected_credentials = [
            'consumer_key',
            'consumer_secret',
            'access_token_key',
            'access_token_secret'
        ]

        for key in expected_credentials:
            if key not in self.credentials:
                msg = "Credential file is missing the field {}, cannot continue...".format(key)
                module_logger.critical(msg)

                raise StoryTellerCredentialParseError(msg)

    def auth(self):

        self.api = twitter.Api(
            consumer_key=self.credentials['consumer_key'],
            consumer_secret=self.credentials['consumer_secret'],
            access_token_key=self.credentials['access_token_key'],
            access_token_secret=self.credentials['access_token_secret']
        )

    def publish_story(self, story_output_data):

        module_logger.info("publishing story as a thread to Twitter")

        module_logger.critical(
            "story_output_data: {}".format(pprint.pformat(story_output_data))
        )

        # module_logger.critical("premature exit!")
        # sys.exit(255)

        module_logger.debug("main tweet data:\n{}".format(
            story_output_data["main_post"]
        ))

        try:
            # TODO: what about title post media?
            title_post = self.api.PostUpdate(story_output_data["main_post"])
            module_logger.info("posted title tweet with ID {}".format(title_post.id))
            lastid = title_post.id
        except twitter.error.TwitterError as e:
            module_logger.exception("Failed to post title tweet, cannot continue.")
            raise e

        threadtweetcounter = 0
        threadtweetcount = len(story_output_data["comment_posts"])

        for thread_tweet in story_output_data["comment_posts"]:
            module_logger.debug("thread tweet text: \n{}".format(
                thread_tweet["text"]
            ))

            threadtweetcounter += 1
            module_logger.info("publishing story element {} of {}".format(threadtweetcounter, threadtweetcount))

            tweet_media = []

            for media_uri in thread_tweet["media"]:

                module_logger.debug("working on media URI {}".format(media_uri))

                if media_uri != "":
                    if media_uri[0:5] == 'data:':
                        mimetype, filedata = datauri_to_data(media_uri)
                        ext = mimetypes.guess_extension(mimetype)
                        f = tempfile.NamedTemporaryFile(prefix='raintale-', suffix=ext, delete=False)
                        f.write(filedata)
                        module_logger.debug("temporary file name is {}".format(f.name))
                        tweet_media.append(f)
                    else:
                        tweet_media.append(media_uri)

            module_logger.info("thread tweet media: \n{}".format(
                tweet_media
            ))

            try:
                element_post = self.api.PostUpdate(
                    status=thread_tweet["text"],
                    media=tweet_media,
                    in_reply_to_status_id=lastid
                )
                lastid = element_post.id
            except twitter.error.TwitterError:

                module_logger.exception(
                    "cannot post tweet for element data {} (note that media will not be shown), skipping".format(thread_tweet["text"])
                )

            for item in tweet_media:
                if type(item) == "tempfile._TemporaryFileWrapper":
                    item.close()
                    os.unlink(item.name)

            module_logger.info("sleeping for 2 seconds for Twitter's benefit...")
            time.sleep(2)

        module_logger.info(
            "Your story has been told on Twitter. Find it at https://twitter.com/{}/status/{}".format(
                title_post.user.screen_name, title_post.id
            )
        )
