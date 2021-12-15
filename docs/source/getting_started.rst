.. _getting_started:

Getting Started With CLI
============================

Raintale allows you to quickly publish your story using a variety of different ``storytellers`` corresponding to different file formats and social media services. The input for Raintale consists of text content and memento URLs (URI-Ms). Raintale will then publish the text verbatim and summarize the archived web pages (e.g., mementos, captures, snapshots, URI-Ms) as surrogates (cards, thumbnails, etc.).

.. note::

    Raintale only works for memento URLs (URI-Ms) from Memento-compliant web archives. It will not work for live web resources or mementos from web archives that do not support the Memento protocol. To create mementos of live web pages, use tools like `the Save Page Now tool at the Internet Archive <https://archive.org/web/>`_, `the ArchiveNow Python utility <https://github.com/oduwsdl/archivenow>`_, or `the Mink Chrome Extension <https://chrome.google.com/webstore/detail/mink-integrate-live-archi/jemoalkmipibchioofomhkgimhofbbem?hl=en-US>`_.


Quickly Creating an HTML Story
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the installation is complete, you will have access to the  ``tellstory`` command. 

Telling an HTML story with Raintale requires three pieces of information:

* the title of your story - this example uses a title of *This is My Story Title*
* a file containing a list of archived web pages (e.g., mementos, captures, snapshots, URI-Ms) - this example uses a file named *story-mementos.txt*
* the name of the file to write your story - this example uses *mystory.html*

Thus, to generate an HTML story with Raintale using the default options, perform the following:

.. code-block:: bash

    tellstory -i story-mementos.txt --storyteller html -o mystory.html --title "This is My Story Title"

Note how the ``--storyteller`` argument instructs Raintale how to tell your story. In this case, we supplied the ``html`` value to tell a story using HTML.

Quickly Creating a Twitter Story
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To create a twitter story, you will need the following:

* the title of your story
* a file containing a list of archived web pages (e.g., mementos, captures, snapshots, URI-Ms)
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

    tellstory -i story_mementos.txt --storyteller twitter --title "This is My Story Title" -c twitter-credentials.yml

Note how, in this case, the ``--storyteller`` argument was supplied the ``twitter`` value. This instructed Raintale to publish a story to Twitter rather than writing it out to a file.

To see a complete list of storytelling capabilities via the ``tellstory`` command refer to :ref:`raintale_options` section.