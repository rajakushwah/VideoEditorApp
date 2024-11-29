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


def TestAccessVideo(unique_id):
    url_video = f"http://127.0.0.1:5001/video/{unique_id}"
    headers_video = {
        'Authorization': 'abc',
    }
    response_video = requests.get(url_video, headers=headers_video)
    print(f"Video access response: {response_video.text}")
    return response_video.text



# x=TestUploadFile()
# x=TestMergeFile()
x=TestAccessVideo("596c74b0-34bf-4028-b77d-0c3fc3d4ea7c")






