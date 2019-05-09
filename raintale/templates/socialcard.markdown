
**{{ title }}**

{% if generated_by is defined %}
**Story By:** {{ generated_by }}</p>
{% endif %}

{% if collection_url is defined %}
**Collection URL:** [{{ collection_url }}]({{ collection_url }})
{% endif %}

{% for surrogate in surrogates %}

---

<img height="96px" src="{{ surrogate.best_image_uri }}">

**[{{ surrogate.title }}]({{ surrogate.urim }})**

Preserved by <img src="{{ surrogate.archive_favicon }}" width="16"> [{{ surrogate.archive_name }}]({{ surrogate.archive_uri }})

{% if surrogate.collection_name is defined %}
Member of the Collection [{{ surrogate.archive_collection_name }}]({{ surrogate.archive_collection_uri }})
{% endif %}

{{ surrogate.snippet }}

<img src="{{ surrogate.original_favicon }}" width="16"> [{{ surrogate.original_domain }}  @  {{ surrogate.memento_datetime }}]({{ surrogate.urim }})

[Other Versions](http://timetravel.mementoweb.org/list/{{ surrogate.memento_datetime_14num }}Z/{{ surrogate.original_uri }}) || [Current Version]({{ surrogate.original_uri }})

{% endfor %}
