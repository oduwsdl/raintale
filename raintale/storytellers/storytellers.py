
from .filetemplate import FileTemplateStoryTeller
from .twitter import TwitterStoryTeller
from .facebook import FacebookStoryTeller
from .video import VideoStoryTeller

storytellers = {
    "facebook": FacebookStoryTeller,
    "twitter": TwitterStoryTeller,
    # "blogger": BloggerStoryTeller,
    "template": FileTemplateStoryTeller,
    "video": VideoStoryTeller
}
