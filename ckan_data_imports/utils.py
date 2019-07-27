#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module has functions that can get data
from an API url and also push data into CKAN,
create CKAN datasets and delete them
"""

import csv
import logging
import requests
import ckanapi

LOGGER = logging.getLogger('ckan_import_default_log')

REMOTE_CONTROL = ckanapi.RemoteCKAN(
    'http://localhost', apikey='7b470db5-0e89-4a02-90a9-6fcdab52a0d5')
DEFRA_AURN_FILES_FOLDER = "/home/kevin/import_scripts/defra_aurn_imports/"

def get_data(url_param, dataset_params):
    """
    Get data from url with params

    Keyword arguments:
    url_param -- url
    dataset_params -- params after the url
    """
    try:
        requested_data = requests.get(url=url_param, params=dataset_params)
        data = requested_data.json()
        if data is None:
            LOGGER.error("Data returned is None")
            return None
        elif "error" in data:
            LOGGER.error("Data returned has an error")
            return None
        else:
            LOGGER.info("Data from %s with parameters was imported", url_param)
            return data
    except Exception as exception_returned:
        LOGGER.error(exception_returned)
        return None

def get_defra_data(file):
    """
    Get data from csv file of defra

    Keyword arguments:
    file -- name of the file
    """
    try:
        with open(DEFRA_AURN_FILES_FOLDER+file) as file_opened:
            res = [{k: int(v) for \
                    k, v in row.items()} for \
                    row in csv.DictReader(file_opened, skipinitialspace=True)]
            reader = csv.DictReader(file_opened)
            list_read = list(reader)
            print(list_read)
        return res
    except Exception as exception_returned:
        LOGGER.error(exception_returned)
        return None

def ckan_insert(resource_id, records_data):
    """
    Insert data into dataset of CKAN

    Keyword arguments:
    resource_id -- id of resource dataset
    records_data -- data to insert
    """
    try:
        pkg = REMOTE_CONTROL.action.datastore_upsert(resource_id=resource_id,
                                                     method="insert",
                                                     records=records_data,
                                                     calculate_record_count=True)
        pkg_json = pkg.json()
        if "success" in pkg_json:
            if pkg_json["success"]:
                LOGGER.info("%s records were inserted into the dataset of id %s",
                            len(records_data),
                            resource_id)
            else:
                if "error" in pkg_json:
                    result_error = pkg_json["error"]
                    if ("__type" in result_error) and ("message" in result_error):
                        LOGGER.error("%s records were not inserted into the dataset of id %s : error type %s , error message %s",
                                     len(records_data),
                                     resource_id,
                                     result_error["__type"],
                                     result_error["message"])
                else:
                    LOGGER.error("%s records were not inserted into the dataset of id %s",
                                 len(records_data),
                                 resource_id)
    except Exception as exception_returned:
        LOGGER.error(exception_returned)

def ckan_upsert(resource_id, records_data):
    """
    Upsert (inserts or updates if primary key exists) data into dataset of CKAN

    Keyword arguments:
    resource_id -- id of resource dataset
    records_data -- data to upsert
    """
    try:
        pkg = REMOTE_CONTROL.action.datastore_upsert(resource_id=resource_id,
                                                     method="upsert",
                                                     records=records_data,
                                                     calculate_record_count=True)
        pkg_json = pkg.json()
        if "success" in pkg_json:
            if pkg_json["success"]:
                LOGGER.info("%s records were upserted into the dataset of id %s",
                            len(records_data),
                            resource_id)
            else:
                if "error" in pkg_json:
                    result_error = pkg_json["error"]
                    if ("__type" in result_error) and ("message" in result_error):
                        LOGGER.error("%s records were not upserted into the dataset of id %s : error type %s , error message %s",
                                     len(records_data),
                                     resource_id,
                                     result_error["__type"],
                                     result_error["message"])
                else:
                    LOGGER.error("%s records were not upserted into the dataset of id %s",
                                 len(records_data),
                                 resource_id)
    except Exception as exception_returned:
        LOGGER.error(exception_returned)

def ckan_delete(resource_id, filters):
    """
    Deletes data from dataset
    Put filters = {} to delete all data

    Keyword arguments:
    resource_id -- id of resource dataset
    filters -- filters to know what data to remove
    """
    try:
        pkg = REMOTE_CONTROL.action.datastore_delete(resource_id=resource_id,
                                                     filters=filters)
        pkg_json = pkg.json()
        if "success" in pkg_json:
            if pkg_json["success"]:
                LOGGER.info("Data was deleted from dataset of id %s",
                            resource_id)
            else:
                if "error" in pkg_json:
                    result_error = pkg_json["error"]
                    if ("__type" in result_error) and ("message" in result_error):
                        LOGGER.error("Data was not deleted from dataset of id %s : error type %s , error message %s",
                                     resource_id,
                                     result_error["__type"],
                                     result_error["message"])
                else:
                    LOGGER.error("Data was not deleted from the dataset of id %s",
                                 resource_id)
    except Exception as exception_returned:
        LOGGER.error(exception_returned)

def ckan_create_from_scratch(package_id, fields_data, primary_keys):
    """
    Create dataset from scratch

    Keyword arguments:
    package_id -- id of the package of datasets
    fields_data -- fields
    primary_keys -- list of fields name which are primary keys
    """
    try:
        pkg = REMOTE_CONTROL.action.datastore_create(resource={'package_id':package_id},
                                                     fields=fields_data,
                                                     primary_key=primary_keys,
                                                     calculate_record_count=True)
        pkg_json = pkg.json()
        if "success" in pkg_json:
            if pkg_json["success"]:
                LOGGER.info("Dataset was created in package of id %s",
                            package_id)
            else:
                if "error" in pkg_json:
                    result_error = pkg_json["error"]
                    if ("__type" in result_error) and ("message" in result_error):
                        LOGGER.error("Dataset was not created in package of id %s : error type %s , error message %s",
                                     package_id,
                                     result_error["__type"],
                                     result_error["message"])
                else:
                    LOGGER.error("Dataset was not created in package of id %s",
                                 package_id)
    except Exception as exception_returned:
        LOGGER.error(exception_returned)

def ckan_create_after_delete(resource_id, fields_data, primary_keys):
    """
    Recreate the structure of the dataset after deleting all data inside.
    Necessary if deleted all the data from dataset.

    Keyword arguments:
    resource_id -- id of the resource dataset
    fields_data -- fields
    primary_keys -- list of fields name which are primary keys
    """
    try:
        pkg = REMOTE_CONTROL.action.datastore_create(resource_id=resource_id,
                                                     fields=fields_data,
                                                     primary_key=primary_keys,
                                                     calculate_record_count=True)
        pkg_json = pkg.json()
        if "success" in pkg_json:
            if pkg_json["success"]:
                LOGGER.info("Structure of dataset of id %s was (re)created",
                            resource_id)
            else:
                if "error" in pkg_json:
                    result_error = pkg_json["error"]
                    if ("__type" in result_error) and ("message" in result_error):
                        LOGGER.error("Structure of dataset of id %s was not (re)created : error type %s , error message %s",
                                     resource_id,
                                     result_error["__type"],
                                     result_error["message"])
                else:
                    LOGGER.error("Structure of dataset of id %s was not (re)created",
                                 resource_id)
    except Exception as exception_returned:
        LOGGER.error(exception_returned)