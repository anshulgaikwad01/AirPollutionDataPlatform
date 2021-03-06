#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module has functions that can get data
from an API url and also push data into CKAN,
create CKAN datasets and delete them
"""

import math
import csv
import logging
import requests
import ckanapi
from utility import config

LOGGER = logging.getLogger('ckan_import_default_log')

REMOTE_CONTROL = ckanapi.RemoteCKAN('http://localhost', apikey=config.apikey)

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

def get_defra_data(file, files_folder_defra_aurn):
    """
    Get data from csv file of defra

    Keyword arguments:
    file -- name of the file
    files_folder_defra_aurn -- folder for the files
    """
    try:
        reader = csv.reader(open(files_folder_defra_aurn+file+".csv"))
        result = []
        for row in reader:
                if (row != ""):
                        #key = row[0]
                        result.append(row[1:])
        return result
    except IOError:
        LOGGER.warning("There is no file "+file+".csv which probably means this station is no longer sustained by DEFRA AURN")    
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
        _ = REMOTE_CONTROL.action.datastore_upsert(resource_id=resource_id,
                                                     method="insert",
                                                     records=records_data,
                                                     calculate_record_count=True)
        LOGGER.info("%s records were inserted into the dataset of id %s",
                    len(records_data),
                    resource_id)
    except Exception as exception_returned:
        LOGGER.error("%s records were not inserted into the dataset of id %s",
                     len(records_data),
                     resource_id)
        LOGGER.error(exception_returned)

def ckan_upsert(resource_id, records_data):
    """
    Upsert (inserts or updates if primary key exists) data into dataset of CKAN

    Keyword arguments:
    resource_id -- id of resource dataset
    records_data -- data to upsert
    """
    try:
        _ = REMOTE_CONTROL.action.datastore_upsert(resource_id=resource_id,
                                                     method="upsert",
                                                     records=records_data,
                                                     calculate_record_count=True)
        LOGGER.info("%s records were upserted into the dataset of id %s",
                    len(records_data),
                    resource_id)
    except Exception as exception_returned:
        LOGGER.error("%s records were not upserted into the dataset of id %s",
                     len(records_data),
                     resource_id)
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
        _ = REMOTE_CONTROL.action.datastore_delete(resource_id=resource_id,
                                                     filters=filters)
        LOGGER.info("Data was deleted from dataset of id %s",
                    resource_id)                   
    except Exception as exception_returned:
        LOGGER.error("Data was not deleted from the dataset of id %s",
                     resource_id)
        LOGGER.error(exception_returned)

def ckan_create_resource(package_id, resource_name, fields_data, primary_keys):
    """
    Create resource 

    Keyword arguments:
    package_id -- id of the package of datasets
    fields_data -- fields
    primary_keys -- list of fields name which are primary keys
    """
    try:
        dict_resource = REMOTE_CONTROL.action.datastore_create(resource={'package_id':package_id, 'name':resource_name},
                                                     fields=fields_data,
                                                     primary_key=primary_keys,
                                                     calculate_record_count=True)
        LOGGER.info("Dataset was created in package of id %s", package_id)
        return dict_resource
    except Exception as exception_returned:
        LOGGER.error("Dataset was not created in package of id %s",
                     package_id)
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
        _ = REMOTE_CONTROL.action.datastore_create(resource_id=resource_id,
                                                     fields=fields_data,
                                                     primary_key=primary_keys,
                                                     calculate_record_count=True)
        LOGGER.info("Structure of dataset of id %s was (re)created",
                    resource_id)
    except Exception as exception_returned:
        LOGGER.error("Structure of dataset of id %s was not (re)created",
                     resource_id)
        LOGGER.error(exception_returned)

def fix_geojson(data):
    """
    Fix geojson values.

    Keyword arguments:
    data - geojson
    """
    coordinates = data["coordinates"]
    tmp = 0
    for k in range(len(coordinates)):
        tmp = coordinates[k]
        if (str(tmp)[::-1].find('.')>5):
            coordinates[k] = math.floor(tmp*10**5)/10**5
    data["coordinates"] = coordinates
    return data

def ckan_create_org(title, name, description, image_url):
    """
    Function to create organisation in the CKAN
    """
    try:
        dict_org = REMOTE_CONTROL.action.organization_create(title=title,name=name,description=description,image_url=image_url)
        LOGGER.info("Creation of Organisation %s was successful", name)
        return dict_org
    except Exception as exception_returned:
        LOGGER.error("Creation of Organisation %s failed", name)
        LOGGER.error(exception_returned)



def ckan_create_package(title, name, private, url, owner_org):
    """
    Function to create Package in the CKAN
    """
    try:
        dict_pkg = REMOTE_CONTROL.action.package_create(title=title,name=name,private=private, url=url, owner_org=owner_org)
        LOGGER.info("Creation of Dataset %s was successful", name)
        return dict_pkg
    except Exception as exception_returned:
        LOGGER.error("Creation of Dataset %s failed", name)
        LOGGER.error(exception_returned)
