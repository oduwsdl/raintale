
<img src="images/raintale-logo.png" width="100px">

# Raintale

Raintale is a utility for publishing social media stories from groups of archived web pages (mementos). Raintale uses MementoEmbed to extract memento information and then publishes a story to the given **storyteller**, a static file or an online social media service.

Raintale accepts the following inputs:
* a file containing a list of memento URLs (URI-Ms) (required)</li>
* a title for your story (required)</li>
* the URL of the underlying collection (optional)</li>
* the author, organization, or algorithm that generated the story (optional)</li>

Raintale supports the following storytellers:
* rawhtml - the HTML that makes up a story, suitable for pasting into a web page or a blogging application such as Blogger
* twitter - the resulting story with be a tweet and its replies, with titles, URLs, memento-datetimes, and images supplied by MementoEmbed

# Running raintale

Raintale uses docker-compose to load and execute all dependencies. To run raintale, do the following:
1. Create a directory on your system
2. Copy docker-compose.yml from this repository into that directory
3. Open a terminal
4. Type: ```docker-compose run raintale bash```
5. In that prompt, type ``raintale-cmd --help`` to find the list of options

For example to create a raw HTML story suitable for pasting, type the following within that prompt:

``
raintale_cmd -i story-mementos.txt --storyteller mystory.html --title "This is My Story Title"	--generated-by "Me"
``

The output will be stored in ``mystory.html``.

To create a twitter story, you will need to create a Twitter app. Log into Twitter from a web browser and visit https://developer.twitter.com/en/apps for more information. Once you have created an app, make a file named ``twitter-credentials.yml`` and fill it with the following content.

``
consumer_key: XXXXXX
consumer_secret: XXXXXX
access_token_key: XXXXXX
access_token_secret: XXXXXX
``

Replace the ``XXXXXX`` values with the corresponding values as displayed on your Twitter app page.

Once that is done, type the following within the Docker prompt:

``
raintale_cmd -i story_mementos.txt --storyteller twitter --title "This is My Story Title"	--generated-by "Me”
``

# Building raintale

Raintale uses ```pip``` for build and installation. From the root of the source code, just type:

```pip install .``` 

to build and install the version from the source code on your machine.

# The future of Raintale

We are working on additional storytellers and story formats. For example, in the near future we plan to add ``thumbnail`` as an story format. Storytellers must be either a file format or an online service that supports an API. The choice in storyteller is highly dependent upon the capabilities and terms of that online service's API.
