Getting Started
===============

Raintale allows you to quickly publish your story using a variety of different ``storytellers`` corresponding to different file formats and social media services. The input for Raintale consists of text content and memento URLs (URI-Ms). Raintale will then publish the text verbatim and summarize the URI-Ms as surrogates (cards, thumbnails, etc.).

.. note::

    Raintale only works for memento URLs (URI-Ms) from Memento-compliant web archives. It will not work for live web resources or mementos from web archives that do not support the Memento protocol. To create mementos of live web pages, use `the Save Page Now tool at the Internet Archive <https://archive.org/web/>`_, `the ArchiveNow Python utility <https://github.com/oduwsdl/archivenow>`_, or `the Mink Chrome Extension <https://chrome.google.com/webstore/detail/mink-integrate-live-archi/jemoalkmipibchioofomhkgimhofbbem?hl=en-US>`_.

Quickly Running Raintale using Docker-Compose
---------------------------------------------

Raintale uses ``docker-compose`` to ensure that users have everything needed to run Raintale quickly. Raintale requires two Docker containers to function:

* `MementoEmbed <https://github.com/oduwsdl/MementoEmbed>`_ - to process mementos, extract content, and produce surrogates
* Raintale - to generate stories from data provided by MementoEmbed

Quickly Creating an HTML Story
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Telling an HTML story with Raintale requires three pieces of information:

* the title of your story - this example uses a title of *This is My Story Title*
* a file containing a list of URI-Ms - this example uses a file named *story-mementos.txt*
* the name of the file to write your story - this example uses *mystory.html*

Thus, to generate an HTML story with Raintale using ``docker-compose`` and the default options, perform the following:

1. Open a terminal on your system
2. Create a directory for your project and change into that directory
3. Download docker-compose.yml from https://raw.githubusercontent.com/oduwsdl/raintale/master/docker-compose.yml to that directory
4. Type the following and press ENTER:

.. code-block:: bash

    docker-compose run raintale tellstory -i story-mementos.txt --storyteller html -o mystory.html --title "This is My Story Title"

Note how the ``--storyteller`` argument instructs Raintale how to tell your story. In this case, we supplied the ``html`` value to tell a story using HTML.

Quickly Creating a Twitter Story
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To create a twitter story, you will need the following:

* the title of your story
* a file containing a list of URI-Ms
* A file containing your Twitter credentials - this example uses ``twitter-credentials.yml``

To acquire Twitter credentials, you will need to create a Twitter app. Log into Twitter from a web browser and visit https://developer.twitter.com/en/apps for more information. Once you have created an app, make a file named ``twitter-credentials.yml``, save it in the same directory, and fill it with the following content.

.. code-block::

    consumer_key: XXXXXX
    consumer_secret: XXXXXX
    access_token_key: XXXXXX
    access_token_secret: XXXXXX

Replace the ``XXXXXX`` values with the corresponding values as displayed on your Twitter app page.

To tell your Twitter story, type the following:

.. code-block:: bash

    docker-compose run raintale tellstory -i story_mementos.txt --storyteller twitter --title "This is My Story Title" -c twitter-credentials.yml

Note how, in this case, the ``--storyteller`` argument was supplied the ``twitter`` value. This instructed Raintale to publish a story to Twitter rather than writing it out to a file.

Setting Up Raintale to Run Natively
-----------------------------------

Raintale is written in Python and communicates to MementoEmbed using the `MementoEmbed Web API <https://mementoembed.readthedocs.io/en/latest/web_api.html>`_. To run natively, Raintale has the following requirements:

* a running MementoEmbed instance - see `the MementoEmbed documentation <https://mementoembed.readthedocs.io/en/latest/index.html>`_ for more information
* Python 3.7
* `pip` version 18 or later

.. note::

    Raintale is developed using MacOS and Linux. We have not yet tested it with Microsoft Windows. We recommend running it using Docker on Microsoft Windows.

To install Raintale natively, do the following:

1. Open a terminal
2. Clone the repository from GitHub by typing: ``git clone https://github.com/oduwsdl/raintale.git``
3. Change into the ``raintale`` directory
4. Type ``pip install .`` to install raintale and all dependencies
5. OPTIONAL for video support - `install ffmpeg <https://ffmpeg.org/download.html>`_

.. note::

    Due to its dependency on MementoEmbed, we have not yet released Raintale via Pypi, but we may do so in the future to improve the ease of installation.
