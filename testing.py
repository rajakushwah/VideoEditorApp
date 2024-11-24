import requests
import os
import json


def TestUploadFile():
    filepath = 'uploads/learn.mp4'
    files = {'video': (os.path.basename(filepath), open(filepath, 'rb'), 'video/mp4')}
    url = "http://127.0.0.1:5001/upload"
    headers = {
        'Authorization': 'abc'
    }
    response = requests.post(url, files=files, headers=headers)
    print(response.text)
    return response.text


x=TestUploadFile()

