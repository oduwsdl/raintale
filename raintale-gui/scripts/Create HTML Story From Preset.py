import argparse
import sys
import logging
import errno

from argparse import RawTextHelpFormatter
from datetime import datetime

from raintale.utils import choose_mementoembed_api, format_data
from raintale.storytellers.filetemplate import FileTemplateStoryTeller
from raintale import package_directory
from raintale.version import __appversion__

# --preset STORYTELLING_PRESET
#                       The preset used for a given story, typically reflecting the 
#                               surrogate used to tell the story and the layout of the story.
#                               * 4image-card
#                         * default
#                         * thumbnails1024
#                         * thumbnails3col
#                         * thumbnails4col
#                         * vertical-bootstrapcards-imagereel


DEFAULT_LOGFILE="./creating-story.log"

parser = argparse.ArgumentParser(prog="{}".format(sys.argv[0]),
    description='Given a list URLs to archived web pages, create an HTML output file based on the selected preset.',
    formatter_class=RawTextHelpFormatter
    )

parser.add_argument('-i', '--input', dest='input_filename',
    required=True,
    help="An input file containing the memento URLs for use in the story.",
    type=argparse.FileType('r')
)

parser.add_argument('--title', dest='title',
    required=True,
    help="The title used for the story."
)

parser.add_argument('--preset', choices = ["default","thumbnails1024", "thumbnails3col", "thumbnails4col", "vertical-bootstrapcards-imagereel"], dest='story_preset',
    required=True,
    help="The preset used for a given story, typically reflecting the surrogate used to tell the story and the layout of the story."
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

def choose_story_template(given_story_template_filename):

    story_template = ""

    story_template_filename = "{}/templates/{}.html".format(
            package_directory, given_story_template_filename)

    logger.info("using story template filename {}".format(story_template_filename))

    try:
        with open(story_template_filename) as f:
            story_template = f.read()

    except FileNotFoundError:
        logger.error("Cannot locate given template filename of {}".format(story_template_filename))
        print("EXITING DUE TO ERROR.")
        sys.exit(errno.EINVAL)

    return story_template

if __name__ == '__main__':
    output_file = "output.html"
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

    input_filename = args.input_filename.name
    storyteller = FileTemplateStoryTeller(output_file)

    mementoembed_api = choose_mementoembed_api(args.mementoembed_api)

    if type(mementoembed_api) == int:
        print("Error Number:" + str(mementoembed_api))
        sys.exit(mementoembed_api)

    story_template_filename = args.story_preset
    story_template = choose_story_template(story_template_filename)

    story_data = format_data(input_filename, args.title, args.collection_url, args.generated_by, parser, args.generation_date)

    #output_location = storyteller.tell_story(story_data, mementoembed_api, story_template)
    #print(output_location)
    end_message = "Done telling your story. Output is available at {}. THE END.".format(output_file)

    logger.info(end_message)
    print(end_message)
