# Video Editor API Client

## Overview

The **Video Editor API Client** is a Python client designed to interact with a local Video Editor API, enabling users to perform operations such as uploading video files, merging multiple videos, and accessing individual video information based on unique identifiers. 

## Features

- Upload video files to the server.
- Merge multiple videos into a single file.
- Retrieve information about specific videos using their unique IDs.


This document provides an overview of the VideoEditorApp API endpoints, their usage, and instructions for running the application locally.


## Prerequisites

1. Install Python 3.8+.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt

3. Clone the repository:
   ```bash
   git clone https://github.com/rajakushwah/VideoEditorApp.git
   cd VideoEditorApp
   
4. Run the application:
   ```flask run
   By default, the app runs on http://127.0.0.1:5001/

# VideoEditorApp API Documentation

## API Endpoints

### 1. Upload Video

- **Endpoint:** `POST /upload`
- **Description:** Upload a video file to the server.
- **Headers:**
  - `Authorization`: API token (e.g., `'abc'`).
- **Request:**
  - `files`: A multipart/form-data containing the video file.
- **Example Code:**

  ```python
  import requests

  filepath = 'path/to/video.mp4'
  url = "http://127.0.0.1:5001/upload"
  headers = {'Authorization': 'abc'}
  files = {'video': (os.path.basename(filepath), open(filepath, 'rb'), 'video/mp4')}

  response = requests.post(url, files=files, headers=headers)
  print(response.text)

### 2. Merge Videos

- **Endpoint:** `POST /merge`
- **Description:** Merge multiple uploaded videos into one file.
- **Headers:**
  - `Authorization`: API token (e.g., `'abc'`).
  - `AContent-Type`: application/json.
- **Request Body (JSON)::**
  - `{
  "filenames": ["file1.mp4", "file2.mp4"]
}`.
- **Example Code:**

  ```python
  import requests
  import json
  
  url = "http://127.0.0.1:5001/merge"
  headers = {'Authorization': 'abc', 'Content-Type': 'application/json'}
  payload = {"filenames": ["new.mp4", "testt.mp4"]}
  
  response = requests.post(url, headers=headers, data=json.dumps(payload))
  print(response.text)


### 2. Access Video

- **Endpoint:** `GET /video/<unique_id>`
- **Description:** Retrieve the processed video by its unique ID.
- **Headers:**
  - `Authorization`: API token (e.g., `'abc'`).
- **Request Body (JSON)::**
  - `Replace <unique_id> in the URL with the actual unique video ID..`
- **Example Code:**

  ```python
  import requests
  
  unique_id = "093ac350-3d25-496f-a73a-a8460c97a646"
  url = f"http://127.0.0.1:5001/video/{unique_id}"
  headers = {'Authorization': 'abc'}
  
  response = requests.get(url, headers=headers)
  print(response.text)


### Notes
- 1. Replace placeholders like file1.mp4, file2.mp4, and unique_id with actual values from your application workflow.
- 2. Ensure the API token (Authorization header) matches the configured value in your application for secure access.
- 3. The merged video file will be saved in the server's directory and accessible via the video_url provided in the response.
- 4. The default API token is configured at param can use 'abc' or  'xyz' **app.config['API_TOKENS'] = {'abc', 'xyz'}**
- 5. configurable limits of size and duration
    - maximum size: e.g. `5 mb`, `25 mb`
    - minimum and maximum duration: e.g. `25 secs`, `5 secs`


### Running Tests
To test the API endpoints:
- 1. Use the provided Python script.
- 2. Uncomment the respective test function calls in the script to test the specific endpoints
 
      - TestUploadFile()
      - TestMergeFile()
      - TestAccessVideo("your-unique-id")

 



