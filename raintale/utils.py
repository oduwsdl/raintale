import logging
import time
import requests
import sys
import os
import errno
import json

from urllib.parse import urlparse

from raintale import package_directory
from raintale.storytellers.storytellers import storytellers, storytellers_without_templates

module_logger = logging.getLogger('raintale.utils')

def test_mementoembed_endpoint(url):

    status = False
    tries = 4

    module_logger.info("testing MementoEmbed endpoint at {}".format(url))

    for i in range(0, tries):

        try:
            requests.get(url)
            status = True
            break
        except requests.ConnectionError:
            retry_time = (i + 1) * 5
            module_logger.error("Failed to connect to MementoEmbed endpoint at {}, sleeping for {} seconds to try again".format(url, retry_time))
            time.sleep(retry_time)

    return status

def choose_mementoembed_api(mementoembed_api_candidates):

    if os.path.exists('/etc/raintale.conf'):

        with open("/etc/raintale.conf") as f:
            for line in f:
                line = line.strip()
                if 'MEMENTOEMBED_ENDPOINT' in line:
                    variable, mementoembed_api = [ s.strip() for s in line.split('=') ]
                    mementoembed_api = mementoembed_api.strip("'")
                    mementoembed_api = mementoembed_api.strip('"')
                    return mementoembed_api

    mementoembed_api = ""

    if type(mementoembed_api_candidates) == list:
        statusii = []

        env_mementoembed_api_candidate = os.getenv("MEMENTOEMBED_API_ENDPOINT")

        if env_mementoembed_api_candidate is not None:
            module_logger.info("adding {} from the environment to the list of candidate MementoEmbed API endpoints".format(env_mementoembed_api_candidate))
            mementoembed_api_candidates.insert(
                0, env_mementoembed_api_candidate
            )

        for url in mementoembed_api_candidates:
            status = test_mementoembed_endpoint(url)
            statusii.append(status)

            if status == True:
                module_logger.info("Successfully connected to MementoEmbed API at {}, using this endpoint".format(url))
                mementoembed_api = url
                break

        if True not in statusii:
            module_logger.error("Failed to connect to MementoEmbed API, cannot continue.")
            sys.exit(errno.EHOSTDOWN)

    else:
        
        module_logger.info("using MementoEmbed endpoint {}, specified via command line flag".format(mementoembed_api_candidates))

        status = test_mementoembed_endpoint(mementoembed_api_candidates)

        if status == False:
            print("Failed to connect to MementoEmbed API, cannot continue.")
            print("Returning status code:" + str(errno.EHOSTDOWN))
            module_logger.error("Failed to connect to MementoEmbed API, cannot continue.")
            return errno.EHOSTDOWN
            #raise Exception("Failed to connect to MementoEmbed API, cannot continue.")
            #sys.exit(errno.EHOSTDOWN)
        else:
            mementoembed_api = mementoembed_api_candidates

    module_logger.info("For building story elements, using MementoEmbedAPI at {}".format(mementoembed_api))

    return mementoembed_api

def format_data(input_filename, title, collection_url, generated_by, parser, generation_date):

    story_data = {}

    module_logger.info("reading story data from file {}".format(input_filename))

    with open(input_filename) as f:

        try:
            story_data = json.load(f)
            
            if 'title' not in story_data:
                parser.error("No story title found in JSON input, a title is required.")
                print("No story title found in JSON input, a title is required.")
                sys.exit(errno.EINVAL)

            if title is not None:
                module_logger.warning("overriding title of '{}' from {} with "
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

            module_logger.warning("story data is not JSON, attempting to read as "
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

            module_logger.info("set story title to {}".format(
                story_data['title']
            ))

            module_logger.info("creating story elements")
            print("Creating story elements")

            for line in f:

                line = line.strip()
                o = urlparse(line)

                if o.scheme in ['http', 'https']:

                    module_logger.debug("adding link {} to story".format(line))

                    element = {
                        'type': 'link',
                        'value': line
                    }

                    story_data['elements'].append(element)

                else:
                    module_logger.warning(
                        "Skipping URL with unsupported scheme: {}".format(line)
                    )

            module_logger.warning("list of memento URLs has been built successfully")
            print("List of memento URLs has been built successfully.")
        
        module_logger.info("data loaded for story with title {}".format(story_data['title']))
        print("data loaded for story with title {}".format(story_data['title']))

    story_data['generation_date'] = generation_date

    return story_data

def choose_story_template(storyteller, preset, given_story_template_filename):

    story_template = ""

    story_template_filename = "{}/templates/{}.{}".format(
        package_directory, preset, storyteller
    )

    module_logger.info("using story template filename {}".format(story_template_filename))

    try:

        with open(story_template_filename) as f:
            story_template = f.read()

    except FileNotFoundError:

        if given_story_template_filename is None:

            if storyteller not in storytellers_without_templates:
                module_logger.error("Unsupported preset {} for storyteller {}".format(preset, storyteller))
                print("EXITING DUE TO ERROR.")
                sys.exit(errno.EINVAL)

        else:
            module_logger.error("Cannot locate given template filename of {}".format(story_template_filename))
            print("EXITING DUE TO ERROR.")
            sys.exit(errno.EINVAL)

    return story_template
