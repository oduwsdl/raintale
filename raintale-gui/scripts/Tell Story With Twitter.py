import argparse
import sys
from argparse import RawTextHelpFormatter
from datetime import datetime

parser = argparse.ArgumentParser(prog="{}".format(sys.argv[0]),
    description='Given a list of story elements, including URLs to archived web pages, create a Twitter thread summarizing the list.',
    formatter_class=RawTextHelpFormatter
)

parser.add_argument('-i', '--input', dest='story_filename',
    required=True,
    help="An input file containing the memento URLs (URI-Ms) for use in the story.",
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

parser.add_argument('--mementoembed_api', dest='mementoembed_api',
    required=False, 
    default=["http://localhost:5550", "http://mementoembed:5550", "http://localhost:5000"],
    help="The URL of the MementoEmbed instance used for generating surrogates"
)

parser.add_argument('--template-file', dest='story_template',
    required=False, 
    help="The file containing the template for the story.",
)

if __name__ == '__main__':
    print("Twitter stories are not yet supported by the Raintale GUI. Please be patient. This functionality will be available soon. If you need Twitter stories, please consult the Raintale CLI at https://raintale.readthedocs.io/en/latest/")
