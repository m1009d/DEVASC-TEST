#!/usr/bin/env python3

"""
This script will retrieve a list of all devices within an organization
via the Meraki Dashboard API.

Meraki is setup hierarchically in a tree structure with Organizations at the
root of the tree. Organizations can have 1-N number of Networks.
Networks then organize Devices and provide for features based on the devices
assigned to that network.

API call to retrieve list devices inside of an organization:
/api/v0/organizations/<organizationId>/devices

For the authentication we need to use the authentication token
which can be obtained via the meraki dashboard.
Once the token is generated, it has to be encoded inside the
"X-Cisco-Meraki-API-Key" header field.

Example of returned data:
[
    {
        "name": "",
        "serial": "Q2EK-S3AA-BXFW",
        "mac": "e0:55:3d:10:42:8a",
        "networkId": "L_646829496481107723",
        "model": "MR84",
        "address": "",
        "lat": 37.4180951010362,
        "lng": -122.098531723022,
        "notes": "",
        "tags": "",
        "lanIp": "192.168.128.3",
        "configurationUpdatedAt": "2021-02-25T10:19:14Z",
        "firmware": "wireless-27-6",
        "url": "https://n149.meraki.com/DNSMB3-sxxxxxtci/n/B5dCcbvc/manage/nodes/new_list/246656701317770"
    }
]

MERAKI DASHBOARD API Learning lab can be accessed here:
https://developer.cisco.com/learning/lab/meraki-02-dashboard-api/

Meraki Dashboard API documentation:
https://developer.cisco.com/meraki/api/
"""

import json
import requests


if __name__ == "__main__":

    # Organization ID 549236 is used in this example but has to be
    # changed according to your organization ID.
    # Please see the example get_organizations.py how to get a list of all
    # organizations.
    org_id = '549236'

    # MERAKI API URL
    # only JSON encoding can be used
    API_URL = f"https://api.meraki.com/api/v0/organizations/{org_id}/devices"

    # Get the token via your Meraki dashboard webpage
    # Storing passwords inside your scripts is not recommended but for the demo
    # purposes it is the easiest way.
    # One recommended way is to export your credentials as an environment
    # variables and then use these variables in your script.
    #
    # Example:
    # import os
    # PASSWORD = os.getenv('MY_SECURE_PASSWORD')
    #
    # Here the environment variable is called 'MY_SECURE_PASSWORD' which
    # contains your secret password.
    token = "6bec40cf957de430a6f1f2baa056b99a4fac9ea0"

    # Prepare the headers for the HTTP GET message
    # with the token included.
    headers = {
        'Content-Type': 'application/json',
        'X-Cisco-Meraki-API-Key': token,
    }

    # In order to see the pagination funtion in action, we can use params
    # and configure to get only 2 devices per HTTP GET request.
    params = {
        'per_page': 2
    }

    # make a global list of all devices
    device_list = []
    def _get_data(**kwargs) -> None:
        """
        Internal recursion function to make the HTTP GET request and
        update the global list named device_list.
        This function handles pagination recursively via calling itself.
        """
        # Make the HTTP GET request to get all devices
        response = requests.get(**kwargs)
        print(f"HTTP GET: {response.url}")

        # Raise an exception if the response is not OK
        if not response.ok:
            print(response.text)
            response.raise_for_status()

        # Extend the global list device_list with the response data
        device_list.extend(response.json())

        # Pagination
        # Meraki Dashboard APIs implement the RFC5988 - Web Linking standard
        # for pagination.
        # By default, the Meraki Dashboard API returns a maximum of 1000 items
        # prior to requiring pagination.
        # In the HTTP Response, an HTTP Header called Link contains information
        # on how to retrieve additional items from the Meraki Dashboard API.
        # First we need to check if the header contains the next key:
        if response.links.get('next'):
            next_url = response.links['next'].get('url')
            kwargs['url'] = next_url
            _get_data(**kwargs)

    # Make the HTTP GET request
    # Calling this function the global list variable device_list will be
    # filled-in with all devices information.
    _get_data(
        url=API_URL,
        headers=headers,
        params=params
    )

    # Print all devices
    print(json.dumps(device_list, indent=4))
