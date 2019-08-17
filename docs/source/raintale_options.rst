.. _raintale_options:

Raintale Options
================

Raintale provides its storytelling capabilities via the ``tellstory`` command. ``tellstory`` supports the following options to control its output:

* ``-i`` or ``--input`` 
    - **required**
    - tells Raintale where to find the story content
    - may be a text file listing URI-Ms or a JSON file for more control
    - formatting this file is covered in :ref:`building_story`
* ``--storyteller``
    - **required**
    - instructs Raintale how to publish the story
    - see :ref:`available_storytellers` for available values
* ``--title`` 
    - **required** for text file input
    - provides the title for the story
    - overrides the ``title`` key provided in JSON input
* ``-c`` or ``--credentials_file``
    - **required** for service storytellers
    - a file containing the credentials needed to publish a story to a given service
* ``-o`` or ``--output-file``
    - **required** for file format storytellers
    - a file for Raintale to write output
* ``--preset`` 
    - instructs Raintale how to format the story using templates that are included with Raintale
    - default value: ``'default'``
* ``--story-template`` 
    - instructs Raintale to use a user-supplied template file rather than an existing ``--preset``
* ``--collection-url``
    - **optional**
    - the URL of the collection from which the story is derived, used by some templates
    - overrides the ``collection_url`` key provided in JSON input
    - default value: ``''``
* ``--generated-by`` 
    - **optional**
    - the name of the algorithm, person, or organization that created this story, used by some templates
    - overrides the ``generated_by`` key provided in JSON input
    - default value: ``''``
* ``--mementoembed_api``
    - **optional**
    - instructs Raintale to use the MementoEmbed instance at the supplied URI
    - if not supplied, Raintale will try the following values in order
        * ``http://localhost:5550``
        * ``http://mementoembed:5550``
        * ``http://localhost:5000``
* ``-l`` or ``--logfile``
    - **optional**
    - if provided, logging output will be written to the supplied file rather than the screen
* ``-v`` or ``--verbose``
    - **optional**
    - instructs Raintale to provide more verbose log output at the DEBUG level
* ``-q`` or ``--quiet``
    - **optional**
    - instructs Raintale to only log warnings or errors

.. _available_storytellers:

Available storytellers
----------------------

Raintale provides the following ``storytellers`` for file formats:

* ``html`` - suitable wherever HTML is used, such as static pages, within Blogger posts, and within curation workflows
* ``markdown`` - suitable for posting to `GitHub gists <https://gist.github.com/>`_
* ``jekyll-html`` and ``jekyll-markdown`` - suitable for use with a `Jekyll site <https://jekyllrb.com/>`_ and posting to `GitHub Pages <https://pages.github.com/>`_
* ``mediawiki`` - for pasting into MediaWiki pages
* ``template`` - a generic storyteller for output to a single file, must have a file specified using the ``--story-template`` parameter
* ``video`` - an **EXPERIMENTAL** storyteller that creates an MPEG video of URI-M content suitable for posting to Twitter or YouTube

To use one of these storytellers, you must also supply the ``-o`` argument specifying the name of the output file.

For social media, Raintale provides the following ``storytellers``:

* ``twitter`` - publishes a story as a Twitter thread, with titles, URLs, memento-datetimes, and images supplied by MementoEmbed
* ``facebook`` - an **EXPERIMENTAL** storyteller that publishes a story as a Facebook thread, with titles, snippets, URLs, and memento-datetimes supplied by MementoEmbed; **it does not yet support image upload**

To use one of these storytellers, you must also supply the ``-c`` argument specifying the name of the file containing credentials in YAML format. For twitter, an example credentials file is shown below:

.. code-block:: text

    consumer_key: XXXXX
    consumer_secret: XXXXX
    access_token_key: XXXXX
    access_token_secret: XXXXX

Replace the values of ``XXXXX`` with the appropriate values for Twitter authentication. Visit https://developer.twitter.com/en/apps for more information on how to generate these values for your Twitter account.

Likewise, for using the **experimental** Facebook storyteller, the credentials file resembles the following:

.. code-block:: text

    page_id: XXXXX
    access_token: XXXXX

Visit https://developers.facebook.com/docs/facebook-login/access-tokens/ for more information on how to generate these values for your Facebook page.


Available presets
-----------------

Using the ``--preset`` option, Raintale provides options for configuring the output of a storyteller. New presets are templates that are provided as part of the Raintale release. New presets are added all of the time. The available presets are visible using ``tellstory --help``.
