import os
import json
import pytest
import tempfile
from app import app as flask_app


@pytest.fixture
def client():
    # Create a temporary database or configuration if needed
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def upload_video(client):
    # Simulate file upload
    filepath = '/Users/rajakushwah/Documents/VideoVerse Assignment/VideoEditorApp/uploads/new.mp4'  # Change to a test video file path
    with open(filepath, 'rb') as f:
        response = client.post('/upload',
                               headers={'Authorization': 'abc'},
                               data={'video': (f, 'new.mp4')})
    return response


def test_upload_file(client, upload_video):
    assert upload_video.status_code == 200  # Change based on your expected status code
    assert 'Video uploaded successfully' in upload_video.data.decode()


def test_merge_file(client):
    payload_merge = {
        "filenames": ["new.mp4", "testt.mp4"]
    }

    response_merge = client.post('/merge',
                                 headers={
                                     'Authorization': 'abc',
                                     'Content-Type': 'application/json'
                                 },
                                 json=payload_merge)
    assert response_merge.status_code == 200  # Change based on your expected status code
    assert 'Merge successful' in response_merge.data.decode()


def test_access_video(client):
    unique_id = "596c74b0-34bf-4028-b77d-0c3fc3d4ea7c"  # Replace with an actual ID you want to test
    response_video = client.get(f'/video/{unique_id}', headers={'Authorization': 'abc'})
    assert response_video.status_code == 200  # Change based on your expected status code
    assert 'Video data' in response_video.data.decode()  # Replace with appropriate checks



def test_e2e(client):
    # Step 1: Upload a video
    upload_response = test_upload_file(client, upload_video)
    assert upload_response.status_code == 200

    # Step 2: Merge the uploaded video with another (simulate the second file if necessary)
    merge_response = test_merge_file(client)
    assert merge_response.status_code == 200

    # Step 3: Access the merged video (assuming you retrieve a valid unique_id after merging)
    unique_id = "596c74b0-34bf-4028-b77d-0c3fc3d4ea7c"  # Change this based on your merge logic
    access_response = test_access_video(client)
    assert access_response.status_code == 200

def test_dummy():
    assert True
