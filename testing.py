import requests
import os
import json


def TestUploadFile():
    filepath = '/Users/rajakushwah/Documents/VideoVerse Assignment/VideoEditorApp/uploads/new.mp4'
    files = {'video': (os.path.basename(filepath), open(filepath, 'rb'), 'video/mp4')}
    url = "http://127.0.0.1:5001/upload"
    headers = {
        'Authorization': 'abc'
    }
    response = requests.post(url, files=files, headers=headers)
    print(response.text)
    return response.text



def TestMergeFile():
    url_merge = "http://127.0.0.1:5001/merge"
    headers_merge = {
        'Authorization': 'abc',
        'Content-Type': 'application/json'
    }
    payload_merge = {
      "filenames": ["new.mp4", "testt.mp4"]
    }

    response_merge = requests.post(url_merge, headers=headers_merge, data=json.dumps(payload_merge))
    print(f"Merge response: {response_merge.text}")
    return response_merge.text

# x=TestUploadFile()
x=TestMergeFile()






