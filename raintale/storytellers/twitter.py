import logging
import mimetypes
import tempfile
import os
import sys

import twitter

from jinja2 import Template

from .storyteller import ServiceStoryteller, get_story_elements, StoryTellerCredentialParseError, split_multipart_template
from ..surrogatedata import get_memento_data, get_template_surrogate_fields, datauri_to_data

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

    def generate_story(self, story_data, mementoembed_api, story_template):

        title_template, element_template, media_template_list = split_multipart_template(story_template)

        story_elements = get_story_elements(story_data)

        module_logger.debug("media_template_list: {}".format(media_template_list))
        
        story_output_data = {
            "main_tweet": "",
            "thread_tweets": []
        }

        story_output_data["main_tweet"] = Template(title_template).render(
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

                    story_output_data["thread_tweets"].append(
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

        module_logger.info("publishing story as a thread to Twitter")

        module_logger.debug("main tweet data:\n{}".format(
            story_output_data["main_tweet"]
        ))

        try:
            # TODO: what about title post media?
            title_post = self.api.PostUpdate(story_output_data["main_tweet"])
            module_logger.info("posted title tweet with ID {}".format(title_post.id))
            lastid = title_post.id
        except twitter.error.TwitterError as e:
            module_logger.exception("Failed to post title tweet, cannot continue.")
            raise e

        threadtweetcounter = 0
        threadtweetcount = len(story_output_data["thread_tweets"])

        for thread_tweet in story_output_data["thread_tweets"]:
            module_logger.debug("thread tweet text: \n{}".format(
                thread_tweet["text"]
            ))

            threadtweetcounter += 1
            module_logger.info("publishing story element {} of {}".format(threadtweetcounter, threadtweetcount))

            tweet_media = []

            for media_uri in thread_tweet["media"]:

                module_logger.debug("working on media URI {}".format(media_uri))

                if media_uri[0:5] == 'data:':
                    mimetype, filedata = datauri_to_data(media_uri)
                    ext = mimetypes.guess_extension(mimetype)
                    f = tempfile.NamedTemporaryFile(prefix='raintale-', suffix=ext, delete=False)
                    f.write(filedata)
                    module_logger.debug("temporary file name is {}".format(f.name))
                    tweet_media.append(f)
                else:
                    tweet_media.append(media_uri)

            module_logger.debug("thread tweet media: \n{}".format(
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

        module_logger.info(
            "Your story has been told on Twitter. Find it at https://twitter.com/{}/status/{}".format(
                title_post.user.screen_name, title_post.id
            )
        )

        # TODO: remember to close the files
