
from .filetemplate import FileTemplateStoryTeller
from .twitter import TwitterStoryTeller
from .facebook import FacebookStoryTeller

storytellers = {
    "facebook": FacebookStoryTeller,
    "twitter": TwitterStoryTeller,
    # "blogger": BloggerStoryTeller,
    "template": FileTemplateStoryTeller
}
