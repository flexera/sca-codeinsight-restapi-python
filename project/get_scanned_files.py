'''
Copyright 2020 Flexera Software LLC
See LICENSE.TXT for full license text
SPDX-License-Identifier: MIT

Author : sgeary  
Created On : Wed Oct 21 2020
File : get_scanned_files.py
'''
import logging
import requests

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------------------#
def get_scanned_files_details(baseURL, projectID, authToken):
    logger.info("Entering get_scanned_files_details")

    currentPage = 1 # Default page number for results

    RESTAPI_BASEURL = baseURL + "/codeinsight/api/"
    ENDPOINT_URL = RESTAPI_BASEURL + "projects/"
    RESTAPI_URL = ENDPOINT_URL + str(projectID) + "/allscannedfiles?includeMD5Hash=true&offset=" + str(currentPage) + "&limit=25"
    logger.debug("    RESTAPI_URL: %s" %RESTAPI_URL)
    
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + authToken}   
       
    ##########################################################################   
    # Make the REST API call with the project data           
    try:
        response = requests.get(RESTAPI_URL, headers=headers)
        logger.info("    Scanned files retreived")
    except requests.exceptions.RequestException as error:  # Just catch all errors
        logger.error(error)
        raise
        
    ###############################################################################
    # We at least received a response from Code Insight so check the status to see
    # what happened if there was an error or the expected data
    if response.status_code == 200:

        scannedFiles = response.json()["data"]
        currentPage = response.headers["Current-page"]
        numPages = response.headers["Number-of-pages"]
        nextPage = int(currentPage) + 1

        while int(nextPage) <= int(numPages):
            RESTAPI_URL = ENDPOINT_URL + str(projectID) + "/allscannedfiles?includeMD5Hash=true&offset=" + str(nextPage) + "&limit=25"
            response = requests.get(RESTAPI_URL, headers=headers)

            nextPage = int(response.headers["Current-page"]) + 1
            scannedFiles += response.json()["data"]
        
        return scannedFiles


    elif response.status_code == 400:
        logger.error("Response code %s - %s" %(response.status_code, response.text))
        print("Response code: %s   -  Bad Request" %response.status_code )
        response.raise_for_status()
    elif response.status_code == 401:
        logger.error("Response code %s - %s" %(response.status_code, response.text))
        print("Response code: %s   -  Unauthorized" %response.status_code )
        response.raise_for_status()    
    else: 
        logger.error("Response code %s - %s" %(response.status_code, response.text))
        response.raise_for_status()