API Documentation for Video Editor Application

Base URL:
All the following API endpoints are relative to the base URL:
http://127.0.0.1:5001/

1. Upload Video File
Uploads a video file to the server.

Endpoint:
POST /upload

Request:
Headers:

Authorization: (required) Your authorization token (e.g., abc).
Body:

Multipart Form Data: The video file is sent as part of a form in the files section.
Example: