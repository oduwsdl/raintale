.. _building_story:

Building Your Story
===================

Raintale stories consist of two main features: a title and a list of memento URLs (URI-Ms). Raintale accepts this information in two formats:

* a simple text file containing a list of URI-Ms to be used in concert with the ``--title`` argument
* a JSON file containing complex information like the list of URI-Ms, the title, surrounding text, and other values for use with a given template

Simple Text File
----------------

Raintale accepts a simple text file containing URI-Ms, like so:

.. code-block::
    :linenos:

    http://wayback.archive-it.org/2950/20120510205501/http://www.thenation.com/blog/167643/may-day-special-occupyusa-blog-may-1-frequent-updates/
    http://wayback.archive-it.org/2950/20120814042704/http://occupyarrests.wordpress.com/

Raintale will generate a surrogate based on each URI-M in this text file and publish them in the order that they exist in this text file. As noted in :ref:`raintale_options`, when using a text file you must also supply a value for the title of the story using the ``--title`` argument.


Complex Story With JSON
-----------------------

Raintale also accepts more complex input in the form of a JSON file. This more complex format allows the story author to supply additional metadata and insert text elements into the story. Below is an example complex story using JSON.

.. code-block::
    :linenos:

    {
        "title": "My Story Title",
        "collection_url": "https://archive.example.com/mycollection",
        "generated_by": "My Curator",
        "metadata": {
            "myKey1": "value1",
            "my-Key2": "value2", 
            "my key 3": "value 3"
        },
        "elements": [
            {
                "type": "text",
                "value": "Livestream from Oakland which remains hot, gas canisters used, arrests, warnings now about more arrests.  \"Chemical agents will be used.\""
            },
            {
                "type": "link",
                "value": "http://wayback.archive-it.org/2950/20120510205501/http://www.thenation.com/blog/167643/may-day-special-occupyusa-blog-may-1-frequent-updates/"
            },
            {
                "type": "text",
                "value": "For Shame: Hundreds Of Arrests Across the Country Today"
            },
            {
                "type": "link",
                "value": "http://wayback.archive-it.org/2950/20120814042704/http://occupyarrests.wordpress.com/"
            }
        ]
    }

Using JSON, the story author can specify the title of the story with the ``title`` key, shown above on line 2. As mentioned in :ref:`raintale_options`, if the ``title`` key is specified here, the ``--title`` parameter does not need to be specified to ``tellstory`` on the command line. The value of the ``--title`` parameter overrules the value of the ``title`` key in the JSON file.

Lines 3 and 4 show how a story author can supply values for ``collection_url`` and ``generated_by``. As noted in :ref:`raintale_options`, if the ``--collection_url`` or ``--generated_by`` arguments are specified to ``tellstory``, then the values supplied with those arguments will override the values in this JSON file.

Lines 5 through 9 demonstrate how the story author can provide additional metadata in the form of a JSON object of keys and values. You can utilize keys from metadata to fill specific values in your template. See the section :ref:`creating_your_own_templates` for more information on how templates work.

Lines 10 through 27 contain the ``elements`` of your story. Each element consists of a JSON object with two keys: ``type`` and ``value``. Raintale will process each element's ``value`` differently based on its ``type``.

The following values are available for ``type``:

* ``text``
    - a raw string to be inserted into your story as is
    - if this text contains markup, then that markup will be inserted as well
    - if including markup in the corresponding ``value``, consider how it will be displayed (e.g., HTML markup with a Twitter storyteller will write HTML tags to your Tweets, which Twitter will not render)
* ``link``
    - a URI-M that will be converted into a surrogate based on the chosen template
    - as mentioned before, only URI-Ms are supported

.. note::

    Additional values for ``type`` may be available in the future based on user needs. Please submit an issue if the existing types do not suit your needs.


