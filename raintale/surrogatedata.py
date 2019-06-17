import re
import logging
import base64
import random

import requests

from datetime import datetime

from requests_futures.sessions import FuturesSession

module_logger = logging.getLogger('raintale.surrogatedata')

fieldname_to_endpoint = {
    
    "timemap_uri": "/services/memento/seeddata/",
    "timegate_uri": "/services/memento/seeddata/",
    "human_timegate_uri": "/services/memento/seeddata/",
    "original_uri": "/services/memento/originalresourcedata/",
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
    "ranked_image_1": "/services/memento/imagedata/",
    "ranked_image_2": "/services/memento/imagedata/",
    "ranked_image_3": "/services/memento/imagedata/",
    "ranked_image_4": "/services/memento/imagedata/",
    "title": "/services/memento/contentdata/",
    "snippet": "/services/memento/contentdata/",
    "memento_datetime": "/services/memento/contentdata/",
    "thumbnail": "/services/product/thumbnail/"

}

class DataURIParseError(Exception):
    pass

class DataURISchemeError(DataURIParseError):
    pass

class DataURIUnsupportedEncoding(DataURIParseError):
    pass

def get_template_surrogate_fields(story_template_string):

    template_surrogate_fields = \
        list(set(sorted(re.findall(r'{{ element.surrogate\.[^}]* }}', story_template_string))))

    return template_surrogate_fields

def png_to_datauri(imgdata):
    datauri = "data:image/png;base64,{}".format(
        base64.encodebytes(imgdata).decode("utf-8")
    )
    return datauri

def datauri_to_data(datauri):

    if datauri[0:5] != 'data:':
        raise DataURISchemeError("Non-data URI submitted for decoding")
    else:
        data = ""

        mimetype, dataheader = datauri[5:].split(';', 1)

        base64header, base64data = dataheader.split(',', 1)

        if base64header != 'base64':
            raise DataURIUnsupportedEncoding
        else:
            return mimetype, base64.decodebytes(base64data.encode("utf-8"))

def get_memento_data(template_surrogate_fields, mementoembed_api, urim):

    memento_data = {}

    if mementoembed_api.endswith('/'):
        mementoembed_api = mementoembed_api[0:-1]

    service_list = []

    for template_surrogate_field in template_surrogate_fields:

        module_logger.debug("template_surrogate_field: {}".format(template_surrogate_field))

        data_field = template_surrogate_field.replace('{{ element.surrogate.', '')
        data_field = data_field.replace(' }}', '')

        module_logger.debug("data field: {}".format(data_field))

        if data_field not in ['urim', 'creation_time', 'memento_datetime_14num']:
            service_list.append( fieldname_to_endpoint[data_field] )

    service_list = list(set(service_list))

    module_logger.debug("service list: {}".format(service_list))

    for service in service_list:

        endpoint = "{}{}{}".format(mementoembed_api, service, urim)

        module_logger.info("querying MementoEmbed endpoint {}".format(endpoint))

        r = requests.get(endpoint)

        if r.status_code == 200:

            if service == '/services/product/thumbnail/':

                memento_data['thumbnail'] = png_to_datauri(r.content)

            elif service == '/services/memento/imagedata/':
                jsondata = r.json()

                # module_logger.debug("jsondata for images: \n{}".format(jsondata))

                for imagecounter in range(0, len(jsondata['ranked images'])):
                    memento_data['ranked_image_{}'.format(imagecounter + 1)] = \
                        jsondata['ranked images'][imagecounter]
                    
            else:
                for key in r.json():
                    memento_data[ key.replace('-', '_') ] = r.json()[key]

        # TODO: what do we do if not 200? what is one service is 200, but another not?
        else:
            module_logger.error("failed to retrieve data from endpoint {}".format(endpoint))

    memento_data['urim'] = urim
    memento_data['creation_time'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    if 'memento_datetime' in memento_data:
        memento_data['memento_datetime_14num'] = \
            datetime.strptime(memento_data['memento_datetime'], '%Y-%m-%dT%H:%M:%SZ').strftime("%Y%m%d%H%M%S")

    return memento_data


class MementoData:

    def __init__(self, template, mementoembed_api):
        self.template = template

        if mementoembed_api.endswith('/'):
            self.mementoembed_api = mementoembed_api[:-1]
        else:
            self.mementoembed_api = mementoembed_api

        self.fields_and_preferences = self._get_field_names_and_preferences()
        # TODO: endpoint_to_fieldname
        self.endpoint_list = self._get_endpoint_list()

        # TODO: consider other backends than RAM
        self.data = {}
        self.urimlist = []

    def _get_field_names_and_preferences(self):

        fields_and_preferences = []

        template_surrogate_fields = get_template_surrogate_fields(
            self.template
        )

        for field in template_surrogate_fields:
            if '|prefer ' in field:
                fieldname, preference = [i.strip() for i in field.split('|prefer ')]
                preference = preference.replace(' }}', '')

            else:
                fieldname = field
                preference = None

            fieldname = fieldname.replace('{{ element.surrogate.', '')
            fieldname = fieldname.replace(' }}', '')

            fields_and_preferences.append(
                (fieldname, preference)
            )
        
        return fields_and_preferences

    def _get_endpoint_list(self):
        
        # what if the same endpoint appears with different preferences?
        # only one call, right?

        endpoints = {}

        for fieldname,pref in self.fields_and_preferences:

            endpoint = self.mementoembed_api + fieldname_to_endpoint[fieldname]

            endpoints.setdefault(endpoint, [])
            
            if pref is not None:
                if pref not in endpoints[endpoint]:
                    endpoints[endpoint].append(pref)

        return endpoints

    def add(self, urim):
        self.urimlist.append(urim)

    def fetch_all_memento_data(self, session=None):
        
        if session is not None:
            fs = FuturesSession(session=session)
        else:
            fs = FuturesSession()

        service_uri_futures = {}

        for urim in self.urimlist:

            module_logger.debug("working on URI-M {}".format(urim))

            for endpoint in self.endpoint_list:

                headers = {}

                service_uri = endpoint + urim

                if len(self.endpoint_list[endpoint]) > 0:
                    headers['Prefer'] = ','.join(self.endpoint_list[endpoint])

                module_logger.debug("issuing request for service URI {}".format(service_uri))

                service_uri_futures.setdefault(urim, {})
                service_uri_futures[urim][service_uri] = \
                    fs.get(service_uri, headers=headers)

        all_memento_data = {}

        def urim_generator(working_list):

            while len(working_list) > 0:
                choice = random.choice(working_list)
                yield choice

        working_service_uri_list = []
        for urim in service_uri_futures:
            for working_service_uri in service_uri_futures[urim]:
                working_service_uri_list.append((urim, working_service_uri))

        module_logger.debug("extracting data from futures: {}".format(service_uri_futures))

        for urim,service_uri in urim_generator(working_service_uri_list):

            if service_uri_futures[urim][service_uri].done():

                module_logger.debug("service URI {} is done".format(service_uri))

                jdata = service_uri_futures[urim][service_uri].result().json()

                for key in jdata:
                    all_memento_data.setdefault(urim, {})
                    all_memento_data[urim][ key.replace('-', '_') ] = jdata[key]

                working_service_uri_list.remove((urim,service_uri))

        self.data = all_memento_data

    def get_memento_data(self, urim, session=None):

        if urim not in self.urimlist:
            self.urimlist.append(urim)

        if urim not in self.data:
            self.fetch_all_memento_data(session=session)

        return self.data[urim]

    def get_sanitized_template(self):
        # TODO: sanitize the template
        pass
