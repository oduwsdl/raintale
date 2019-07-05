
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

---

<div style="text-align: right">
Story visualized with the help of [Raintale](https://github.com/oduwsdl/raintale)
</div>
