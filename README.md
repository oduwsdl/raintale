# raintale

Raintale is a utility for creating social media stories from groups of archived web pages (mementos). Raintale uses MementoEmbed to extract memento information and then publishes a story to the given **storyteller**, a static file or an online social media service.

Raintale accepts the following inputs:
* a file containing a list of memento URLs (URI-Ms) (required)</li>
* a title for your story (required)</li>
* the URL of the underlying collection (optional)</li>
* the author, organization, or algorithm that generated the story (optional)</li>

Raintale creates stories using different formats. These formats influence the content available to a given storyteller. Raintale supports the following story formats:
* social card - content from cards for individual mementos, like those seen in social media and produced by MementoEmbed

Raintale supports the following storytellers:
* rawhtml - the HTML that makes up a story, suitable for pasting into a web page or a blogging application such as Blogger
* twitter - the resulting story with be a tweet and its replies, with titles, URLs, memento-datetimes, and images supplied by MementoEmbed


