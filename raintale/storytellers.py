import logging
import re

import twitter
import requests

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

from jinja2 import Template, Environment, meta

from .surrogatedata import get_memento_data, get_template_surrogate_fields

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

    def get_story_elements(self):

        try:
            story_elements = self.story_data['elements']
            return story_elements
        except KeyError:
            msg = "Cannot tell story. Story does not contain elements. "
            module_logger.exception(msg)
            raise StoryTellerStoryParseError(msg)

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

        story_elements = self.get_story_elements()

        story_output += '<p><h1>{}</h1></p>\n'.format(
            self.story_data['title'])

        if self.story_data['generated_by'] is not None:
            story_output += '<p><strong>Story By:</strong> {}</p>\n'.format(
                self.story_data['generated_by'])
        
        if self.story_data['collection_url'] is not None:
            story_output += '<p><strong>Collection URL:</strong> <a href="{}">{}</a></p>\n'.format(
                self.story_data['collection_url'], 
                self.story_data['collection_url']
            )

        module_logger.info("preparing to iterate through {} story "
            "elements".format(len(story_elements)))

        elementcounter = 1

        for element in story_elements:

            module_logger.info("processing element {} of {}".format(
                elementcounter, len(story_elements))
            )

            module_logger.debug("examining story element {}".format(element))

            try:

                if element['type'] == 'link':

                    raw_element_html = \
                        self.storygenerator.get_urielement_rawhtml(
                            element['value'])

                    story_output += "<hr>\n<p>\n{}\n</p>\n".format(raw_element_html)

                else:
                    module_logger.warn(
                        "skipping unsupported story element type of {}".format(
                            element['type']
                        ))

            except KeyError:

                module_logger.error(
                    "cannot process story element data of {}, skipping".format(element)
                )
            
            elementcounter += 1

        with open(output_filename, 'w') as f:
            f.write(story_output)

class TwitterStoryTeller(StoryTeller):

    def tell_story(self):

        module_logger.debug("telling story using TwitterStoryTeller")

        api = twitter.Api(
            consumer_key=self.credentials['consumer_key'],
            consumer_secret=self.credentials['consumer_secret'],
            access_token_key=self.credentials['access_token_key'],
            access_token_secret=self.credentials['access_token_secret']
        )

        story_elements = self.get_story_elements()

        module_logger.info("preparing to iterate through {} story "
            "elements".format(len(story_elements))
        )

        title_tweet_elements = []

        title_tweet_elements.append(self.story_data['title'])

        if self.story_data['generated_by'] is not None:
            title_tweet_elements.append(
                "Story by: {}".format(self.story_data['generated_by'])
            )

        if self.story_data['collection_url'] is not None:
            title_tweet_elements.append(self.story_data['collection_url'])

        try:
            title_post = api.PostUpdate(status="\n\n".join(title_tweet_elements))
            module_logger.info("posted title tweet with ID {}".format(title_post.id))
            lastid = title_post.id

        except twitter.error.TwitterError as e:
            module_logger.exception("Failed to post title tweet, cannot continue.")
            raise e

        for element in story_elements:

            module_logger.debug("examining story element {}".format(element))

            try:

                if element['type'] == 'link':

                    urim = element['value']

                    module_logger.debug(
                        "getting story data for URI-M {}".format(urim))

                    element_data = self.storygenerator.get_urielement_data(urim)

                    if element_data['errordata'] is None:

                        module_logger.debug("acquired story element data {}".format(
                            element_data
                        ))

                        # the URL is 23 characters, regardless
                        # datetimes are in the format 2012-10-09T00:56:56Z, length 20
                        # this leaves 280 - 23 - 20 = 237 chars for title
                        tweet_length = len(element_data['memento-datetime']) + \
                            len(element_data['title']) + 23
                        
                        if tweet_length > 280:
                            page_title = "{}...".format(page_title[0:234])
                        else:
                            page_title = element_data['title']

                        tweet_text = "{}\n\n{}\n\n{}".format(
                            page_title,
                            element_data['memento-datetime'],
                            urim
                        )

                        module_logger.debug("tweet text is {}".format(tweet_text))

                        module_logger.debug("using image of {}".format(
                            element_data['image']
                        ))

                        if element_data['image'][0:5] == 'data:':
                            module_logger.info("skipping data URI image for URI-M {}".format(urim))
                            element_post = api.PostUpdate(
                                status=tweet_text,
                                in_reply_to_status_id=lastid
                            )
                        else:
                            element_post = api.PostUpdate(
                                status=tweet_text,
                                media=element_data['image'],
                                in_reply_to_status_id=lastid
                            )

                        module_logger.debug(
                            "posted story element as tweet data {}".format(element_post)
                        )

                        module_logger.info(
                            "posted story element as tweet with ID {}".format(element_post.id)
                        )

                        lastid = element_post.id
                    
                    else:
                        module_logger.error("failure to process link element {}, reason: {}".format(
                            urim, element_data['errordata']
                        ))

                else:

                    module_logger.warn(
                        "skipping unsupported story element type of {}".format(
                            element['type']
                        ))

            except KeyError:

                module_logger.exception(
                    "cannot process story element data of {}, skipping".format(element)
                )

            except twitter.error.TwitterError:

                module_logger.exception(
                    "cannot post tweet for story element {}, skipping".format(element)
                )

class BloggerStoryTeller(StoryTeller):

    def tell_story(self):

        module_logger.debug("telling story using BloggerStoryTeller")

        client_config = {
            "installed": {
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://accounts.google.com/o/oauth2/token",
                "redirect_uris": [],
                "client_id": self.credentials['clientid'],
                "client_secret": self.credentials['clientsecret']
            }
        }

        flow = InstalledAppFlow.from_client_config(
            client_config,
            scopes=['https://www.googleapis.com/auth/blogger'])

        credentials = flow.run_console()

        blogger_service = build('blogger', 'v3', credentials=credentials)

        story_elements = self.get_story_elements()

        blog_post_content = '<p><strong>Story By: </strong>{}</p><p>Collection URL: <a href="{}">{}</a></p>'.format(
            self.story_data['generated_by'], 
            self.story_data['collection_url'], self.story_data['collection_url']
        )

        story_elements = self.get_story_elements()

        for element in story_elements:

            module_logger.debug("examining story element {}".format(element))

            try:

                if element['type'] == 'link':

                    urim = element['value']

                    module_logger.debug(
                        "getting story data for URI-M {}".format(urim)
                    )

                    raw_element_html = self.storygenerator.get_urielement_rawhtml(urim)

                    blog_post_content += "<p>\n{}\n</p>\n".format(raw_element_html)
                
                else:
                    module_logger.warn(
                        "skipping unsupported story element type of {}".format(
                            element['type']
                        ))

            except KeyError:

                module_logger.exception(
                    "cannot process story element data of {}, skipping".format(element)
                )

        module_logger.info("posting story to blog ID {}".format(self.credentials['blogid']))

        request_body = {
            "kind": "blogger#post",
            "title": self.story_data['title'],
            "content": blog_post_content
        }

        r = blogger_service.posts().insert(
            blogId=self.credentials['blogid'],
            body=request_body
        ).execute()

        module_logger.info("blog post should be available at {}".format(r['url']))

class FileTemplateStoryTeller(StoryTeller):

    def tell_story(self):

        module_logger.debug("telling story using FileTemplateStoryTeller")

        try:
            with open(self.credentials['story_template']) as f:
                story_template_string = f.read()
        except KeyError:
            msg = "Credentials do not contain a story template filename"
            module_logger.exception(msg)
            raise StoryTellerCredentialParseError(msg)

        try:
            output_filename = self.credentials['output_filename']
        except KeyError:
            msg = "Credentials do not contain output filename"
            module_logger.exception(msg)
            raise StoryTellerCredentialParseError(msg)

        story_elements = self.get_story_elements()

        surrogates = []

        module_logger.info("preparing to iterate through {} story "
            "elements".format(len(story_elements)))

        elementcounter = 1

        template_surrogate_fields = get_template_surrogate_fields(story_template_string)

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
                        self.storygenerator.mementoembed_api, 
                        urim)

                    surrogates.append(memento_data)

            except KeyError as e:

                raise e

                module_logger.error(
                    "cannot process story element data of {}, skipping".format(element)
                )

            elementcounter += 1

        with open(output_filename, 'w') as f:
            f.write(Template(story_template_string).render(
                title=self.story_data['title'],
                generated_by=self.story_data['generated_by'],
                collection_url=self.story_data['collection_url'],
                surrogates=surrogates
            ))


storytellers = {
    "twitter": TwitterStoryTeller,
    "blogger": BloggerStoryTeller,
    "template": FileTemplateStoryTeller
}

storytelling_services = [
    "twitter",
    "blogger"
]
