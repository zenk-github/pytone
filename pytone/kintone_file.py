import requests
import json

class KintoneFile:
    def __init__(self, api_token, domain):
        self.api_token  = api_token
        self.rootURL   = 'https://{}.cybozu.com/k/v1/file.json'.format(domain)
        self.headers   = {
            "X-Cybozu-API-Token": self.api_token,
        }

    def downloadFile(self, fileKey):
        body = {
            'fileKey': fileKey
        }
        try:
            response = requests.get(self.rootURL, json=body, headers=self.headers)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException:
            raise Exception(response.json())

    def uploadFile(self, file):
        body = {
            'file': file
        }
        try:
            response = requests.post(self.rootURL, headers=self.headers, files=body)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            raise Exception(response.json())