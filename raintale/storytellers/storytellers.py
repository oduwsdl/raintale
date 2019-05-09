
from .filetemplate import FileTemplateStoryTeller
from .twitter import TwitterStoryTeller

storytellers = {
    "twitter": TwitterStoryTeller,
    # "blogger": BloggerStoryTeller,
    "template": FileTemplateStoryTeller
}
