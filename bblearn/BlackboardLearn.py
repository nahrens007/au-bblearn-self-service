import requests
# For AuthToken
import datetime
import time

import json

requests.packages.urllib3.disable_warnings()

# class responsible for managing authentication with the bb server
class AuthToken():
    target_url = ''

    def __init__(self, URL, key, secret):

        self.KEY = key
        self.SECRET = secret
        self.PAYLOAD = {
            'grant_type':'client_credentials'
        }

        self.TOKEN = None
        self.target_url = URL
        self.EXPIRES_AT = ''

    def getKey(self):
        return self.KEY

    def getSecret(self):
        return self.SECRET

    def setNewToken(self):
        oauth_path = '/learn/api/public/v1/oauth2/token'
        OAUTH_URL = self.target_url + oauth_path

        session = requests.session()

        # Authenticate
        r = session.post(OAUTH_URL, data=self.PAYLOAD, auth=(self.KEY, self.SECRET), verify=False)

        if r.status_code == 200:
            parsed_json = json.loads(r.text)
            self.TOKEN = parsed_json['access_token']
            self.EXPIRES = parsed_json['expires_in']
            m, s = divmod(self.EXPIRES, 60)

            self.NOW = datetime.datetime.now()
            self.EXPIRES_AT = self.NOW + datetime.timedelta(seconds = s, minutes = m)

        return r.status_code

    def setToken(self):
        if self.setNewToken() == 200:
            if self.isExpired(self.EXPIRES_AT):
                self.setToken()

        else:
            # Auth error!!!
            self.EXPIRES = 0
            m, s = divmod(self.EXPIRES, 60)

            self.NOW = datetime.datetime.now()
            self.EXPIRES_AT = self.NOW + datetime.timedelta(seconds = s, minutes = m)

    def getToken(self):
        #if token time is less than a one second then
        # print that we are pausing to clear
        # re-auth and return the new token
        if self.isExpired(self.EXPIRES_AT):
            self.setToken()
        return self.TOKEN

    def getTokenExpires(self):
        return self.EXPIRES_AT

    def revokeToken(self):
        revoke_path = '/learn/api/public/v1/oauth2/revoke'
        revoke_URL = self.target_url + revoke_path

        self.PAYLOAD = {
            'token':self.TOKEN
        }

        if self.TOKEN != '':
            for keys,values in self.PAYLOAD.items():
                print("\t\t\t" + keys + ":" + values)
            session = requests.session()

            # revoke token
            r = session.post(revoke_URL, data=self.PAYLOAD, auth=(self.KEY, self.SECRET), verify=False)

            if r.status_code == 200:
                # successful revoke
                pass
            else:
                # could not revoke
                pass
        else:
            # Token is not currently set
            pass


    def isExpired(self, expiration_datetime):
        expired = False

        time_left = (expiration_datetime - datetime.datetime.now()).total_seconds()
        if time_left < 1:
            expired = True

        return expired

# class responsible for providing an interface with the bb server, using AuthTocken class
class LearnInterface:
    def __init__(self, url, key, secret):

        self.server_url = url
        self.auth_instance = AuthToken(url, key, secret)
        self.auth_instance.setToken()
        self.session = requests.session()

    #return the response from the post call
    def post(self, url, json_data):
        return self.session.post(self.server_url + url,data=json_data,auth=(self.auth_instance.getKey(),self.auth_instance.getSecret()),verify=False)

    #return the response of the get call
    def get(self, url):
        return self.session.get(self.server_url + url, headers={'Authorization':'Bearer ' + self.auth_instance.getToken()}, verify=False)

    #return the response of the delete call
    def delete(self, url):
        return self.session.delete(self.server_url + url, auth=(self.auth_instance.getKey(),self.auth_instance.getSecret()), verify=False)

    #return the response of the patch call
    def patch(self, url, json_data):
        return self.session.patch(self.server_url + url,data=json_data,auth=(self.auth_instance.getKey(),self.auth_instance.getSecret()),verify=False)

    def getTokenExpires(self):
        return self.auth_instance.getTokenExpires()
