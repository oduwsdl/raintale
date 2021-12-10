import argparse
import sys
import logging

from argparse import RawTextHelpFormatter
from datetime import datetime

from raintale.version import __appversion__

from raintale.utils import choose_mementoembed_api, choose_story_template, format_data
from raintale.storytellers.video import VideoStoryTeller


DEFAULT_LOGFILE="./creating-story.log"

parser = argparse.ArgumentParser(prog="{}".format(sys.argv[0]),
    description='Given a list URLs to archived web pages, create a video file summarizing the URLs through images and text.',
    formatter_class=RawTextHelpFormatter
)

parser.add_argument('-i', '--input', dest='story_filename',
    required=True,
    help="An input file containing URLs of archived web pages (e.g., mementos, captures, snapshots, URI-Ms) for use in the story.",
    type=argparse.FileType('r')
)

parser.add_argument('--title', dest='title',
    required=True,
    help="The title used for the story. If JSON story file is submitted, this value will be overriden by the title in that JSON input."
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


if __name__ == '__main__':
    output_file = "output.mp4"

    args = parser.parse_args()

    start_message = "Beginning Raintale to tell your story. ONCE UPON A TIME..."

    # set up logging for the rest of the system
    logger = logging.getLogger(__name__)
    logging.basicConfig( 
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        level=logging.INFO,
        filename=DEFAULT_LOGFILE)

    print(start_message)
    logger.info(start_message)
    #print("My current directory is: " + os.getcwd())

    story_filename = args.story_filename.name

    storyteller_class = VideoStoryTeller

    storyteller = storyteller_class(output_file)

    mementoembed_api = choose_mementoembed_api([])
    print("using MementoEmbed at {}".format(mementoembed_api))

    story_template = choose_story_template("video", "default", None)

    print("generating video story")
    story_data = format_data(story_filename, args.title, args.collection_url, args.generated_by, parser, args.generation_date)

    output_location = storyteller.tell_story(story_data, mementoembed_api, story_template)

    end_message = "Done telling your video story. Output is available at {}. THE END.".format(output_location)

    logger.info(end_message)
    print(end_message)
