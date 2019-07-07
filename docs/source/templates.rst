Creating Your Own Templates
===========================

Raintale allows the user to supply their own templates to format a story. Each template can be in a text-based format. Examples of text-based formats are HTML, XML, Markdown, and JSON. Raintale's presets are templates and you can view the files in the templates directory of the `Raintale GitHub <https://github.com/oduwsdl/raintale/tree/master/raintale/templates>`_ repository. Templates are built using an extension of the Jinja2 template engine. Because the format is an extension, not all Raintale templates are interoperable with Jinja2.

A Simple Template
-----------------

As noted in :ref:`building_story`, Raintale, at a minimum, accepts a list of memento URLs (URI-Ms) from which to build your story. An example template below creates a four-column row of thumbnails for each URI-M in the story.

.. code-block:: jinja
    :linenos:
    
    <p><h1>{{ title }}</h1></p>

    {% if generated_by is defined %}
    <p><strong>Story By:</strong> {{ generated_by }}</p>
    {% endif %}

    {% if collection_url is defined %}
    <p><strong>Collection URL:</strong> <a href="{{ collection_url }}">{{ collection_url }}</a></p>
    {% endif %}

    <hr>

    <table border="0">
    <tr>
    {% for element in elements %}

    {% if element.type == 'link' %}

        <td><img src="{{ element.surrogate.thumbnail }}"></td>

        {% if loop.index is divisibleby 4 %}
            </tr><tr>
        {% endif %}

    {% else %}

    <!-- Element type {{ element.type }} is unsupported by the thubmnails3col template -->

    {% endif %}

    {% endfor %}

In this example, the ``{{ title }}`` variable will be filled by the parameter of the ``--title`` argument of the ``tellstory`` command. The same for the ``{{ generated_by }}`` and ``{{ collection_url }}`` variables and their corresponding ``tellstory`` arguments.

The URI-M list supplied to the ``tellstory`` command is converted into a data structure that is stored in the ``elements`` variable. The template engine will iterate through this list using the Jinja2 code ``{% for element in elements %}`` on line 15 and the ``{% endfor %}`` on line 31 closing this loop.

If the URI-M list is supplied as a simple text file, then the ``element.type`` of each story element is set to ``link``. Other element types, such as ``text``, are covered in :ref:`building_story`. Your template is required to support at least element type, otherwise there will be no story. Only the ``link`` element type has any extensive configuration.

In this example, the ``{{ element.surrogate.thumbnail }}`` variable (line 19) contains the thumbnail corresponding to the URI-M discovered at that point in the loop. Let's break this variable down. The ``element`` portion is the iterator served by the Jinja2 loop by the line 15  statement ``{% for element in elements %}``. The ``surrogate`` portion of this variable indicates that we are looking for a feature of the memento behind the URI-M which in this case is a ``thumbnail``. 

If the user supplies 16 URI-Ms and information about the Archive-It collection *Occupy Movement 2011/2012*, then the template above will generate a story using thumbnails, as seen below.

.. image:: images/thumbcol4story_2950.png

There are many other features than ``thumnbail`` available for URI-Ms. Note that Raintale only provides features for URI-Ms from Memento-compliant web archives. It will not work for live web resources. In the following section, we cover more memento features that can be used in your stories.

A More Complex Example
----------------------

The following example displays how one can use Raintale templates with Markdown.

.. code-block:: jinja
    :linenos:

    **{{ title }}**

    {% if generated_by is defined %}
    **Story By:** {{ generated_by }}</p>
    {% endif %}

    {% if collection_url is defined %}
    **Collection URL:** [{{ collection_url }}]({{ collection_url }})
    {% endif %}

    {% if metadata is defined %}

    {% for key, value in metadata.items() %}

    **{{ key|title }}**: {{ value }}

    {% endfor %}

    {% endif %}

    {% for element in elements %}

    ---

    {% if element.type == 'link' %}

    <img height="96px" src="{{ element.surrogate.best_image_uri }}">

    **[{{ element.surrogate.title }}]({{ element.surrogate.urim }})**

    Preserved by <img src="{{ element.surrogate.archive_favicon }}" width="16"> [{{ element.surrogate.archive_name }}]({{ element.surrogate.archive_uri }})

    {% if element.surrogate.archive_collection_name is not none %}
    Member of the Collection [{{ element.surrogate.archive_collection_name }}]({{ element.surrogate.archive_collection_uri }})
    {% endif %}

    {{ element.surrogate.snippet }}

    <img src="{{ element.surrogate.original_favicon }}" width="16"> [{{ element.surrogate.original_domain }}  @  {{ element.surrogate.memento_datetime }}]({{ element.surrogate.urim }})

    [Other Versions](http://timetravel.mementoweb.org/list/{{ element.surrogate.memento_datetime_14num }}Z/{{ element.surrogate.original_uri }}) || [Current Version]({{ element.surrogate.original_uri }})

    {% else %}

    {{ element.text }}

    {% endif %}

    {% endfor %}

In this example, we highlight some additional functionality. If you supply a JSON story that contains a ``metadata`` key to a `JSON object <https://en.wikipedia.org/wiki/JSON#Data_types_and_syntax>`_, then the key value pairs for that object will be rendered within the loop from lines 13 to 17.

The loop for the story elements starts on line 21. For the ``link`` element type, lines 25 - 42 utilize the many features available in Raintale to render a URI-M into a surrogate for storytelling. Each of these varabiles is prefixed with ``element.surrogate.``. The next section contains the full list of available variables.

Line 45 shows how a template can handle a ``text`` element type via the ``element.text`` variable.

Available Surrogate Variables
-----------------------------

All surrogate variables begin with ``element.surrogate.`` in order to indicate that they correspond to a story element and are intended to produce a surrogate of a URI-M.

Some of these surrogate variables support *preferences* that allow you to control their output. Preferences are specified within a Raintale variable by the use of ``|prefer `` where the final space after prefer is significant. For example:

.. code-block::

    {{ element.surrogate.image|prefer rank=3 }}

The above example would replace the value of the variable with the 3 :superscript:`rd` best scoring image from the memento. If multiple preferences are desired, they are separated by ``,`` with no space in between.

.. note::

    If a Raintale preference is used in a template, it is no longer a valid Jinja2 template and will only work with Raintale.

.. note::

    Preferences are different from Jinja2 *filters* because filters modify a value after it has been calculated. Preferences instruct Raintale how to generate the value for the variable before it is calculated. Raintale does not currently support using both Preferences and Jinja2 fitlers in the same template, but it is planned for future releases.

* ``element.surrogate.archive_collection_id``
    - the ID of the collection containing this URI-M
    - only works with URI-Ms from public Archive-It collections
* ``element.surrogate.archive_collection_name``
    - the name of the collection containing this URI-M
    - only works with URI-Ms from public Archive-It collections
* ``element.surrogate.archive_collection_uri``
    - the URI of the collection containing this URI-M
    - only works with URI-Ms from public Archive-It collections
* ``element.surrogate.archive_favicon``
    - the URI of the favicon of the archive containing this URI-M
    - preferences:
        - ``datauri_favicon=yes`` - instructs Raintale to convert the favicon into a data URI, making the story larger in bytes by also freeing the display of the image from Internet connection issues
* ``element.surrogate.archive_name``
    - the uppercase name of the domain name of the archive containing this URI-M
* ``element.surrogate.archive_uri``
    - the URI of the archive containing this URI-M
* ``element.surrogate.best_image_uri``
    - the URI of the best image found in the memento using the MementoEmbed image scoring equation
    - may be deprecated in the future in favor of ``element.surrogate.image|prefer rank=1``
* ``element.surrogate.first_memento_datetime``
    - the datetime of the *earliest* memento for this resource at the web archive containing this URI-M
* ``element.surrogate.first_title``
    - the title pulled from the HTML of the *earliest* memento for this resource at the web archive containing this URI-M
* ``element.surrogate.first_urim``
    - the URI-M of the *earliest* memento for this resource at the web archive containing this URI-M
* ``element.surrogate.image``
    - provides the i :superscript:`th` best image found in the memento using the MementoEmbed image scoring equation
    - this allows a user to include multiple images in a surrogate from a memento
    - preferences:
        - ``rank=i`` where ``i`` is the rank of the image
        - default value: ``rank=0``
* ``element.surrogate.last_memento_datetime``
    - the datetime of the *latest* memento for this resource at the web archive containing this URI-M
* ``element.surrogate.last_title``
    - the title pulled from the HTML of the *latest* memento for this resource at the web archive containing this URI-M
* ``element.surrogate.last_urim``
    - the URI-M of the *latest* memento for this resource at the web archive containing this URI-M
* ``element.surrogate.memento_count``
    - the number of other mementos for this same resource at the web archive containing this URI-M
* ``element.surrogate.memento_datetime``
    - the memento-datetime of the memento, when it was captured by the web archive
* ``element.surrogate.memento_datetime_14num``
    - provides memento-datetime in ``YYYYMMDDHHMMSS`` format
    - a specially datetime format for use in some web archive URIs
    - this variable is under consideration for deprecation once Jinja2 filters are supported
* ``element.surrogate.metadata``
    - the metadata provided for the seed of this URI-M
    - provides a JSON object of keys and values corresponding to the metadata fields present at the archive
    - only works with URI-Ms from public Archive-It collections
* ``element.surrogate.original_domain``
    - the domain of the original resource for this URI-M
* ``element.surrogate.original_favicon``
    - the favicon corresponding to the original resource for this URI-M
    - preferences:
        - ``datauri_favicon=yes`` - instructs Raintale to convert the favicon into a data URI, making the story larger in bytes by also freeing the image from Internet connection issues
* ``element.surrogate.original_linkstatus``
    - the status of the link at the time the story was generated
* ``element.surrogate.original_uri``
    - the URI of the resource from which the memento was created
    - the URI of the live version of the resource, if still present, outside of web archives
    - known as **URI-R** in Memento protocol terminology
* ``element.surrogate.snippet``
    - the best text extracted from the memento via MementoEmbed
* ``element.thumbnail``
    - provides a thumbnail generated by MementoEmbed for the given URI-M as a data URI 
    - preferences:
        - ``viewport_width`` - the width of the viewport (in pixels) of the browser capturing the snapshot (upper bound is 5120px)
        - ``viewport_height`` - the height of the viewport (in pixels) of the browser capturing the snapshot (upper bound is 2880px)
        - ``thumbnail_width`` - the width of the thumbnail in pixels, the thumbnail will be reduced in size to meet this requirement (upper bound is 5210px)
        - ``thumbnail_height`` - the height of the thumbnail in pixels, the thumbnail will be reduced in size to meet this requirement (upper bound is 2880px)
        - ``timeout`` - how long MementoEmbed should wait for the thumbnail to finish generating before issuing an error (upper bound is 5 minutes)
* ``element.surrogate.timegate_uri``
    - the URI of the Memento TimeGate corresponding to the resource
    - with a TimeGate a Memento client can request a different memento for the same resource
    - known as **URI-G** in Memento protocol terminology
* ``element.surrogate.timemap_uri``
    - the URI of the Memento TimeMap corresponding to the resource
    - a TimeMap lists the URI-Ms and mement-datetimes of other mementos for this resource
    - known as **URI-T** in Memento protocol terminology
* ``element.surrogate.title``
    - the text of the title extracted from the HTML of the memento
* ``element.surrogate.urim``
    - the URI-M of this memento

