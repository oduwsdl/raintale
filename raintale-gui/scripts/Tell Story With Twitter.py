import argparse
import sys
import os
import logging
import time
import errno
import json
import pathlib

from urllib.parse import urlparse
from argparse import RawTextHelpFormatter
from datetime import datetime

import requests

from yaml import load, Loader

from raintale.storytellers.storytellers import storytellers, storytellers_without_templates
from raintale import package_directory
from raintale.version import __appversion__

from raintale.storytellers.twitter import TwitterStoryTeller

DEFAULT_LOGFILE="./creating-story.log"


parser = argparse.ArgumentParser(prog="{}".format(sys.argv[0]),
    description='Given a list of URLs to archived web pages, create a Twitter thread summarizing the list.',
    formatter_class=RawTextHelpFormatter
)

parser.add_argument('-i', '--input', dest='story_filename',
    required=True,
    help="An input file containing the memento URLs (URI-Ms) for use in the story.",
    type=argparse.FileType('r')
)

parser.add_argument('-c', '--credentials_file', dest='credentials_file',
    required=True,
    help="The file containing the credentials needed to use a storytelling service, in YAML format.",
    type=argparse.FileType('r')
)

parser.add_argument('--title', dest='title',
    required=True,
    help="The title used for the story. If JSON story file is submitted, this value will be overriden by the title in that JSON input."
)

parser.add_argument('--story-template', dest='story_template_filename',
    required=False, default=None,
    help="The file containing the template for the story.",
    type=argparse.FileType('r')
)

parser.add_argument('--collection-url', dest='collection_url',
    required=False, default=None,
    help="The URL of the collection from which the story is derived."
)

parser.add_argument('--generated-by', dest='generated_by',
    required=False, default=None,
    help="The name of the algorithm or person who created this story."
)

parser.add_argument('--generation-date', dest='generation_date',
    required=False, default=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    help="The generation date for this story, in YYYY-mm-ddTHH:MM:SS format. Default value is now."
)

parser.add_argument('--mementoembed_api', dest='mementoembed_api',
    required=False, 
    default=["http://localhost:5550", "http://mementoembed:5550", "http://localhost:5000"],
    help="The URL of the MementoEmbed instance used for generating surrogates"
)


def test_mementoembed_endpoint(url):

    status = False
    tries = 4

    logger.info("testing MementoEmbed endpoint at {}".format(url))

    for i in range(0, tries):

        try:
            requests.get(url)
            status = True
            break
        except requests.ConnectionError:
            retry_time = (i + 1) * 5
            logger.error("Failed to connect to MementoEmbed endpoint at {}, sleeping for {} seconds to try again".format(url, retry_time))
            time.sleep(retry_time)

    return status


def choose_mementoembed_api(mementoembed_api_candidates):

    mementoembed_api = ""

    if type(mementoembed_api_candidates) == list:
        statusii = []

        env_mementoembed_api_candidate = os.getenv("MEMENTOEMBED_API_ENDPOINT")

        if env_mementoembed_api_candidate is not None:
            logger.info("adding {} from the environment to the list of candidate MementoEmbed API endpoints".format(env_mementoembed_api_candidate))
            mementoembed_api_candidates.insert(
                0, env_mementoembed_api_candidate
            )

        for url in mementoembed_api_candidates:
            status = test_mementoembed_endpoint(url)
            statusii.append(status)

            if status == True:
                logger.info("Successfully connected to MementoEmbed API at {}, using this endpoint".format(url))
                mementoembed_api = url
                break

        if True not in statusii:
            logger.error("Failed to connect to MementoEmbed API, cannot continue.")
            sys.exit(errno.EHOSTDOWN)

    else:
        
        logger.info("using MementoEmbed endpoint {}, specified via command line flag".format(mementoembed_api_candidates))

        status = test_mementoembed_endpoint(mementoembed_api_candidates)

        if status == False:
            logger.error("Failed to connect to MementoEmbed API, cannot continue.")
            sys.exit(errno.EHOSTDOWN)
        else:
            mementoembed_api = mementoembed_api_candidates

    logger.info("For building story elements, using MementoEmbedAPI at {}".format(mementoembed_api))

    return mementoembed_api

def format_data(input_filename, title, collection_url, generated_by, parser, generation_date):

    story_data = {}

    logger.info("reading story data from file {}".format(input_filename))

    with open(input_filename) as f:

        try:
            story_data = json.load(f)
            
            if 'title' not in story_data:
                parser.error("No story title found in JSON input, a title is required.")
                sys.exit(errno.EINVAL)

            if title is not None:
                logger.warning("overriding title of '{}' from {} with "
                    "title '{}' supplied as argument".format(
                        story_data['title'], input_filename, title
                    ))
                story_data['title'] = title

            if 'generated_by' not in story_data:
                story_data['generated_by'] = generated_by

            if 'collection_url' not in story_data:
                story_data['collection_url'] = collection_url

            if 'story image' not in story_data:
                story_data['story image'] = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD//gBHRmlsZSBzb3VyY2U6IGh0dHBzOi8vY29tbW9ucy53aWtpbWVkaWEub3JnL3dpa2kvRmlsZTpCbGFja19jb2xvdXIuanBn/9sAQwAGBAUGBQQGBgUGBwcGCAoQCgoJCQoUDg8MEBcUGBgXFBYWGh0lHxobIxwWFiAsICMmJykqKRkfLTAtKDAlKCko/9sAQwEHBwcKCAoTCgoTKBoWGigoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgo/8AAEQgA8AC0AwEiAAIRAQMRAf/EABcAAQEBAQAAAAAAAAAAAAAAAAABAgj/xAAbEAEBAAEFAAAAAAAAAAAAAAAAAUEhMWFxgf/EABUBAQEAAAAAAAAAAAAAAAAAAAAB/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8A5WAAAAAAAAAAAAAAAAAAABQBQBRAAAEAAAAAAAAAAAARQFUEVEABQBRAAAABUAAAAAAQAAFBQAAAQAFAAEAAAAAAARAAAAAAAAFAFBFEAFVZqIAgAAAAAgAgAAAAAAAAKgKKAgAqgCCAAAKACIAAAAAAAAAAAAKgCiKKAKIRUAAAARAAAAAAAAAAAABUAURVUABBUAAAARAAAAAAAAAAAFBAUARVUAQEVFBRAAEQAAAAAAAAAAVAFEUABVAEABQABBUAARAAAAAAAABQVQBAAUABAAUAAABBUAAEAUEBQQFRQBQAAAAFnYCAAAAAAAAIoAAAAAAAAAAgAKAAAAAAACAAoAAAAAIACgAAAACggALQAAAQFBBUAFQAUBAAAABQEBQRQA9ABUau6CoKCIBgAAAAAAAAAMHAAKKgKImFCCqAD//Z"

        except json.JSONDecodeError:

            logger.warning("story data is not JSON, attempting to read as "
                "a list of memento URLs in a text file")

            if title == None:
                parser.error("Text file format requires a title be supplied on the command line.")
                sys.exit(errno.EINVAL)

            f.seek(0)
            story_data['title'] = title
            
            # if collection_url is not None:
            #     logger.debug("storing given collection URL of {}".format(collection_url))
            story_data['collection_url'] = collection_url

            # if generated_by is not None:
            #     logger.debug("storing generated by value of {}".format(generated_by))
            story_data['generated_by'] = generated_by

            story_data['story image'] = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD//gBHRmlsZSBzb3VyY2U6IGh0dHBzOi8vY29tbW9ucy53aWtpbWVkaWEub3JnL3dpa2kvRmlsZTpCbGFja19jb2xvdXIuanBn/9sAQwAGBAUGBQQGBgUGBwcGCAoQCgoJCQoUDg8MEBcUGBgXFBYWGh0lHxobIxwWFiAsICMmJykqKRkfLTAtKDAlKCko/9sAQwEHBwcKCAoTCgoTKBoWGigoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgo/8AAEQgA8AC0AwEiAAIRAQMRAf/EABcAAQEBAQAAAAAAAAAAAAAAAAABAgj/xAAbEAEBAAEFAAAAAAAAAAAAAAAAAUEhMWFxgf/EABUBAQEAAAAAAAAAAAAAAAAAAAAB/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8A5WAAAAAAAAAAAAAAAAAAABQBQBRAAAEAAAAAAAAAAAARQFUEVEABQBRAAAABUAAAAAAQAAFBQAAAQAFAAEAAAAAAARAAAAAAAAFAFBFEAFVZqIAgAAAAAgAgAAAAAAAAKgKKAgAqgCCAAAKACIAAAAAAAAAAAAKgCiKKAKIRUAAAARAAAAAAAAAAAABUAURVUABBUAAAARAAAAAAAAAAAFBAUARVUAQEVFBRAAEQAAAAAAAAAAVAFEUABVAEABQABBUAARAAAAAAAABQVQBAAUABAAUAAABBUAAEAUEBQQFRQBQAAAAFnYCAAAAAAAAIoAAAAAAAAAAgAKAAAAAAACAAoAAAAAIACgAAAACggALQAAAQFBBUAFQAUBAAAABQEBQRQA9ABUau6CoKCIBgAAAAAAAAAMHAAKKgKImFCCqAD//Z"

            story_data['metadata'] = {}

            story_data['elements'] = []

            logger.info("set story title to {}".format(
                story_data['title']
            ))

            logger.info("creating story elements")

            for line in f:

                line = line.strip()
                o = urlparse(line)

                if o.scheme in ['http', 'https']:

                    logger.debug("adding link {} to story".format(line))

                    element = {
                        'type': 'link',
                        'value': line
                    }

                    story_data['elements'].append(element)

                else:
                    logger.warning(
                        "Skipping URL with unsupported scheme: {}".format(line)
                    )

            logger.warning("list of memento URLs has been built successfully")
        
        logger.info("data loaded for story with title {}".format(story_data['title']))

    story_data['generation_date'] = generation_date

    return story_data

def choose_story_template(storyteller, preset):

    story_template = ""

    story_template_filename = "{}/templates/{}.{}".format(
        package_directory, preset, storyteller
    )

    logger.info("using story template filename {}".format(story_template_filename))

    try:

        with open(story_template_filename) as f:
            story_template = f.read()

    except FileNotFoundError:

        if given_story_template_filename is None:

            if storyteller not in storytellers_without_templates:
                logger.error("Unsupported preset {} for storyteller {}".format(preset, storyteller))
                print("EXITING DUE TO ERROR.")
                sys.exit(errno.EINVAL)

        else:
            logger.error("Cannot locate given template filename of {}".format(story_template_filename))
            print("EXITING DUE TO ERROR.")
            sys.exit(errno.EINVAL)

    return story_template

if __name__ == '__main__':
    args = parser.parse_args()

    start_message = "Beginning raintale to tell your story."

    # set up logging for the rest of the system
    logger = logging.getLogger(__name__)
    logging.basicConfig( 
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        level=logging.INFO,
        filename=DEFAULT_LOGFILE)

    print(start_message)
    logger.info(start_message)

    story_filename = args.story_filename.name
    credentials_filename = args.credentials_file.name

    storyteller_class = TwitterStoryTeller

    storyteller = None

    if credentials_filename is None:
        parser.error(
            "storyteller of type {} requires a credentials file, please supply a credentials file with the -c option".format(
                args.storyteller)
        )
    else:
        storyteller = storyteller_class(credentials_filename)

    mementoembed_api = choose_mementoembed_api(args.mementoembed_api)

    if args.story_template_filename is None:
        story_template = choose_story_template("twitter", "default")
    else:
        story_template = args.story_template_filename.read()

    story_data = format_data(story_filename, args.title, args.collection_url, args.generated_by, parser, args.generation_date)

    output_location = storyteller.tell_story(story_data, mementoembed_api, story_template)

    end_message = "Done telling your story on Twitter. Output is available at {}. THE END.".format(output_location)

    logger.info(end_message)
    print(end_message)