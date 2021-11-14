import argparse
import sys
import os
import logging
import errno

from argparse import RawTextHelpFormatter
from datetime import datetime

from raintale.utils import choose_mementoembed_api, format_data
from raintale.version import __appversion__
from raintale import package_directory
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

# parser.add_argument('--mementoembed_api', dest='mementoembed_api',
#     required=False, 
#     default=["http://localhost:5550", "http://mementoembed:5550", "http://localhost:5000"],
#     help="The URL of the MementoEmbed instance used for generating surrogates"
# )

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

        logger.error("Cannot locate given template filename of {}".format(story_template_filename))
        print("EXITING DUE TO ERROR.")
        sys.exit(errno.EINVAL)

    return story_template, story_template_filename

if __name__ == '__main__':

    print("Beginning parse.")
    
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

    print("")
    storyteller_class = TwitterStoryTeller

    storyteller = None

    if credentials_filename is None:
        parser.error(
            "storyteller of type {} requires a credentials file, please supply a credentials file with the -c option".format(
                args.storyteller)
        )
    else:
        storyteller = storyteller_class(credentials_filename)

    print("The story file & credentials were successfully provided.")
    mementoembed_api = choose_mementoembed_api([])

    if args.story_template_filename is None:
        story_template, story_template_filename = choose_story_template("twitter", "default")
    else:
        story_template = args.story_template_filename.read()
        story_template_filename = args.story_template_filename.name

    print("applying story template file {}".format(story_template_filename))
    print("applying credentials file {}".format(os.path.basename(credentials_filename)))

    print("formatting story data from story file {}".format(os.path.basename(story_filename)))
    
    story_data = format_data(story_filename, args.title, args.collection_url, args.generated_by, parser, args.generation_date)

    print("generating Twitter story")

    output_location = storyteller.tell_story(story_data, mementoembed_api, story_template)

    end_message = "Done telling your story on Twitter. Output is available at {}. THE END.".format(output_location)

    logger.info(end_message)
    print(end_message)
