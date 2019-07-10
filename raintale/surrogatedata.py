import re
import logging
import base64
import random
import json
import pprint

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
    "image": "/services/memento/imagedata/",
    "title": "/services/memento/contentdata/",
    "snippet": "/services/memento/contentdata/",
    "memento_datetime": "/services/memento/contentdata/",
    "thumbnail": "/services/product/thumbnail/",
    "imagereel": "/services/product/imagereel/"
}

calculated_fields = {
    "urim",
    "creation_time",
    "memento_datetime_14num"
}

raintale_preferences_per_field = {
    "image": [
        "rank",
        "datauri"
    ]
}

# TODO: preference for any image as data URI
raintale_specific_preferences = [
    "rank",
    "datauri"
]

raintale_ranking_services = [
    "/services/"
]

class MementoEmbedRequestError(Exception):
    pass

class DataURIParseError(Exception):
    pass

class DataURISchemeError(DataURIParseError):
    pass

class DataURIUnsupportedEncoding(DataURIParseError):
    pass

def get_futures_session(session=None):

    if session is not None:
        fs = FuturesSession(session=session)
    else:
        fs = FuturesSession()

    return fs

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

def get_field_value(data, preferences, base_fieldname):

    module_logger.debug("getting value for fieldname {} using preferences {}".format(base_fieldname, preferences))

    if base_fieldname == "creation_time":
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    # TODO: how to hanlde memento_datetime_14num?
        
    elif base_fieldname == "thumbnail":
        return png_to_datauri(data)

    elif base_fieldname == "image":
        
        imageuri = None
        prefdict = {
            "rank": 1,
            "datauri": "yes"
        }

        for preference in preferences:

            var, rank = preference.split('=')

            prefdict[var] = rank

        # handle rank first
        
        jdata = json.loads(data)
        ranked_images = jdata["ranked images"]

        try:
            imageuri = ranked_images[ int(prefdict['rank']) - 1 ]
        except IndexError:
            imageuri = ""

        # TODO: this seems like too much for this function to handle
        # if prefdict["datauri"] == "yes":
        #     # download the content
        #     r = requests.get(imageuri)
        #     # convert it to a data uri
        #     if r.status_code == 200:
        #         imageuri = png_to_datauri(r.content)
        #     else:
        #         module_logger("got a status code of {} for image at URI {}, refusing to convert to data URI".format(r.status_code, imageuri))

        return imageuri

    elif base_fieldname == "imagereel":

        return png_to_datauri(data)

    else:

        me_fieldname = base_fieldname.replace('_', '-')

        return json.loads(data)[me_fieldname]

class MementoData:

    def __init__(self, template_string, mementoembed_api):
        self.mementoembed_api = mementoembed_api
        self.template_string = template_string
        self._data = {}
        self._urimlist = []
        self._mementodata = {}

        module_logger.debug("initializing memento data class with template:\n\n{}\n\n".format(template_string))

        self._template_surrogate_fields = get_template_surrogate_fields(template_string)

    def add(self, urim):
        
        for field in self._template_surrogate_fields:
            working_dict = {}

            fieldname = field.replace('{{ element.surrogate.', '').replace(' }}', '')
            preferences = None

            if '|prefer ' in fieldname:
                fieldname, preferences = [ i.strip() for i in fieldname.split('|prefer ') ]

            working_dict["full endpoint"] = None
            working_dict["endpoint path"] = None

            rtprefs = []
            meprefs = []

            if fieldname not in calculated_fields:

                if preferences is not None:

                    for preference in [ i.strip() for i in preferences.split(',') ]:

                        prefname = preference

                        if '=' in preference:
                            prefname, value = [ i.strip() for i in preference.split('=') ]

                        if fieldname in raintale_preferences_per_field:
                            if prefname in raintale_preferences_per_field[fieldname]:
                                rtprefs.append(preference)
                            else:
                                meprefs.append(preference)
                        else:
                            meprefs.append(preference)

                endpoint = fieldname_to_endpoint[fieldname]
                working_dict["endpoint path"] = endpoint
                working_dict["full endpoint"] = "{}{}{}".format(
                    self.mementoembed_api,
                    endpoint,
                    urim
                    )
            
            working_dict["base field name"] = fieldname
            working_dict["Raintale preferences"] = tuple(rtprefs)
            working_dict["MementoEmbed preferences"] = tuple(meprefs)
            working_dict["sanitized field name"] = field.replace('|prefer ', '__prefer__').replace('=', '_').replace(',', '_').replace('{{ element.surrogate.', '').replace(' }}', '')

            self._data[ ( field, urim ) ] = working_dict
            self._urimlist.append(urim)

    def get_sanitized_template(self):

        fieldlist_to_replacements = {}

        for field, urim in self._data:
            fieldlist_to_replacements[field] = "{{ element.surrogate." + self._data[(field, urim)]["sanitized field name"] + " }}"

        sanitized_template = self.template_string

        for field in fieldlist_to_replacements:
            sanitized_template = sanitized_template.replace(
                field, fieldlist_to_replacements[field]
            )

        return sanitized_template

    def get_endpoints_and_preferences_with_fields(self):

        endpoint_data = {}

        for template_surrogate_field, urim in self._data:
            # print("evaluating {} for URI-M {}".format(template_surrogate_field, urim))

            if template_surrogate_field != "{{ element.surrogate.urim }}":
                
                endpoint = self._data[ (template_surrogate_field, urim) ]["full endpoint"]
                base_fieldname = self._data[ (template_surrogate_field, urim) ]["base field name"]

                if base_fieldname not in calculated_fields:

                    me_preferences = self._data[ (template_surrogate_field, urim) ]["MementoEmbed preferences"]

                    endpoint_data.setdefault( (endpoint, me_preferences), {} )
                    endpoint_data[ (endpoint, me_preferences) ].setdefault("fields", []).append(
                        (template_surrogate_field, urim)
                    )
            
        return endpoint_data

    def issue_future_requests(self, endpoint_data, futuressession):

        endpoint_keys = list(endpoint_data.keys())

        for endpoint, me_preferences in endpoint_keys:

            if endpoint is not None:
                headers = {}

                if len(me_preferences) > 0:
                    headers['Prefer'] = ','.join(me_preferences)

                endpoint_data[ (endpoint, me_preferences) ]["future request"] = futuressession.get(endpoint, headers=headers)

        return endpoint_data

    def fetch_all_memento_data(self, session=None):

        fs = get_futures_session(session=session)

        future_requests = {}

        module_logger.debug("current template data structure is: \n{}\n".format(
            pprint.pformat(self._data, indent=4)
        ))

        future_requests = self.get_endpoints_and_preferences_with_fields()
        future_requests = self.issue_future_requests(future_requests, fs)

        def request_generator(working_list):

            while len(working_list) > 0:
                choice = random.choice(working_list)
                yield choice

        request_working_list = list(future_requests.keys())

        for endpoint, me_preferences in request_generator(request_working_list):

            if "future request" in future_requests[ (endpoint, me_preferences) ]:
                request = future_requests[ (endpoint, me_preferences) ]["future request"]

                if request is not None:

                    if request.done() is True:

                        module_logger.info("request for {} is ready to be reviewed".format(endpoint))

                        result = request.result()

                        module_logger.debug("status is {}".format(result.status_code))

                        if result.status_code == 200:

                            module_logger.debug("fields for this endpoint with preferences: {}".format(
                                future_requests[ (endpoint, me_preferences) ]["fields"]
                            ))

                            # TODO: this should be going through the content for just endpoint, me_preferences
                            for fieldname, urim in future_requests[ (endpoint, me_preferences) ]["fields"]:
                                self._mementodata.setdefault(
                                    urim, {
                                        "urim": urim,
                                        "creation_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                                    })
                                rt_preferences = self._data[ (fieldname, urim) ]["Raintale preferences"]
                                base_fieldname = self._data[ (fieldname, urim) ]["base field name"]

                                module_logger.debug("attempting to set memento data value '{}' using base field name '{}' and Raintale preferences '{}'".format(
                                    self._data[ (fieldname, urim) ]["sanitized field name"],
                                    base_fieldname,
                                    rt_preferences
                                ))
                                module_logger.debug("mementodata was {}\n\n".format(
                                    pprint.pformat( self._mementodata )
                                ))

                                try:
                                    
                                    self._mementodata[urim][
                                        self._data[ (fieldname, urim) ]["sanitized field name"]
                                    ] = get_field_value(result.content, rt_preferences, base_fieldname)

                                except json.decoder.JSONDecodeError as e:
                                    module_logger.exception("Failed to process output from MementoEmbed for URI-M {} at endpoint {}, quitting...".format(urim, endpoint))

                                except KeyError as e:
                                    module_logger.exception("Got error at endpoint {}: {}".format(endpoint, e))

                                module_logger.debug("mementodata is now {}\n\n".format(
                                    pprint.pformat( self._mementodata )
                                ))

                            module_logger.debug("done with endpoint {} with preferences {}, removing...".format(endpoint, me_preferences))

                            request_working_list.remove( (endpoint, me_preferences) )

                        else:
                            module_logger.debug("cannot process response with output of {}".format(
                                result.content
                            ))
                            module_logger.debug("cannot process response with request headers of {}".format(
                                pprint.pformat(result.request.headers, indent=4)
                            ))
                            
                            request_working_list.remove( (endpoint, me_preferences) )

                            raise MementoEmbedRequestError("failed to get a good response from MementoEmbed at {}, something went wrong, try rerunning Raintale again...".format(endpoint))
                    
                    else:
                        module_logger.debug("waiting for request to endpoint {} with preferences {} to complete".format(
                            endpoint, me_preferences
                        ))
                
            module_logger.debug("working list is now {}".format(request_working_list))

        for urim in self._mementodata:
            
            if 'memento_datetime' in self._mementodata[urim]:
                self._mementodata[urim]['memento_datetime_14num'] = \
                    datetime.strptime(self._mementodata[urim]['memento_datetime'], '%Y-%m-%dT%H:%M:%SZ').strftime("%Y%m%d%H%M%S")

        module_logger.debug("mementodata stabilized at {}".format(pprint.pformat(self._mementodata, indent=4)))


    def get_memento_data(self, urim, session=None):
        
        if urim not in self._urimlist:
            self.add(urim)

        if urim not in self._mementodata:
            self.fetch_all_memento_data(session=session)

        module_logger.debug("mementodata: {}".format(
            pprint.pformat(self._mementodata, indent=4)
        ))

        return self._mementodata[urim]


