import re
import logging
import base64

from datetime import datetime

import requests

module_logger = logging.getLogger('raintale.surrogatedata')

fieldname_to_endpoint = {
    
    "timemap_uri": "/services/memento/seeddata/",
    "timegate_uri": "/services/memento/seeddata/",
    "human_timegate_uri": "/services/memento/seeddata/",
    "original_uri": "/services/memento/seeddata/",
    "memento_count": "/services/memento/seeddata/",
    "first_memento_datetime": "/services/memento/seeddata/",
    "last_memento_datetime": "/services/memento/seeddata/",
    "first_urim": "/services/memento/seeddata/",
    "last_urim": "/services/memento/seeddata/",
    "first_title": "/services/memento/seeddata/",
    "last_title": "/services/memento/seeddata/",
    "metadata": "/services/memento/seeddata/",
    "original_domain": "/services/memento/originalresourcedata/",   
    "original_favicon": "/services/memento/originalresourcedata/",
    "original_linkstatus": "/services/memento/originalresourcedata/",
    "archive_uri": "/services/memento/archivedata/",
    "archive_name": "/services/memento/archivedata/",
    "archive_favicon": "/services/memento/archivedata/",
    "archive_collection_id": "/services/memento/archivedata/",
    "archive_collection_name": "/services/memento/archivedata/",
    "archive_collection_uri": "/services/memento/archivedata/",
    "best_image_uri": "/services/memento/bestimage/",
    "title": "/services/memento/contentdata/",
    "snippet": "/services/memento/contentdata/",
    "memento_datetime": "/services/memento/contentdata/",
    "thumbnail": "/services/product/thumbnail/"

}

def get_template_surrogate_fields(story_template_string):

    template_surrogate_fields = \
        list(set(sorted(re.findall(r'{{ surrogate\.[^}]* }}', story_template_string))))

    return template_surrogate_fields

def png_to_datauri(data):

    return 

def get_memento_data(template_surrogate_fields, mementoembed_api, urim):

    memento_data = {}

    if mementoembed_api.endswith('/'):
        mementoembed_api = mementoembed_api[0:-1]

    service_list = []

    for template_surrogate_field in template_surrogate_fields:

        data_field = template_surrogate_field.replace('{{ surrogate.', '')
        data_field = data_field.replace(' }}', '')

        if data_field not in ['urim', 'creation_time', 'memento_datetime_14num']:
            service_list.append( fieldname_to_endpoint[data_field] )

    service_list = list(set(service_list))

    module_logger.debug("service list: {}".format(service_list))

    for service in service_list:

        endpoint = "{}{}{}".format(mementoembed_api, service, urim)

        module_logger.info("querying endpoint {}".format(endpoint))

        r = requests.get(endpoint)

        if r.status_code == 200:

            if service == '/services/product/thumbnail/':
                memento_data['thumbnail'] = "data:image/png;base64,{}".format(
                    base64.encodebytes(r.content).decode("utf-8")
                )
            else:
                for key in r.json():
                    memento_data[ key.replace('-', '_') ] = r.json()[key]

        # TODO: what do we do if not 200? what is one service is 200, but another not?

    memento_data['urim'] = urim
    memento_data['creation_time'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    if 'memento_datetime' in memento_data:
        memento_data['memento_datetime_14num'] = \
            datetime.strptime(memento_data['memento_datetime'], '%Y-%m-%dT%H:%M:%SZ').strftime("%Y%m%d%H%M%S")

    return memento_data
