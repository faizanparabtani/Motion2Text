# Motion2Text

A computer vision application that converts air handwriting into digital notes using Google Cloud Vision AI and the Evernote API.

## Overview

Motion2Text tracks a colored object through a webcam and uses it as a virtual pen. When you're done writing, the canvas is sent to Google Cloud Vision for handwriting recognition and the transcribed text is saved directly to your Evernote account.

## Features

- Real-time colored object tracking via HSV segmentation and contour detection
- Handwriting recognition powered by Google Cloud Vision AI
- Saves notes as text or image attachments to Evernote
- On-screen trackbars for adjusting HSV thresholds to match your environment

## Tech Stack

| Component | Technology |
|---|---|
| Motion Tracking | OpenCV |
| Text Recognition | Google Cloud Vision AI |
| Note Storage | Evernote API |
| Image Processing | NumPy |

## How It Works

The webcam feed is converted to HSV color space and masked to isolate the tracked object. Morphological operations (erosion and dilation) reduce noise before contour detection identifies the pointer. Stroke paths accumulate on a canvas that mirrors the live feed. On save, the canvas is submitted to the Vision AI `document_text_detection` endpoint, and the result is structured as ENML and pushed to Evernote via `NoteStore.createNote`.

## Demo

![Real-time tracking view](https://user-images.githubusercontent.com/52961945/127783200-9f035f2d-4352-451a-95c8-3f44ab01800e.png)

*Real-time motion tracking*

![Evernote output](https://user-images.githubusercontent.com/52961945/127783208-5ee2fa45-e4fa-462d-848e-222b902b23c7.png)

*Resulting Evernote note with transcribed handwriting*

## Setup

**Prerequisites:** Python 3, a GCP account with Vision API enabled, and an Evernote sandbox developer token.

```bash
pip install opencv-python evernote3 google-cloud-vision numpy pandas
```

1. Place your GCP service account credentials file as `visionapi.json` in the project root
2. Set your Evernote developer token in `doodle.py`:
   ```python
   developer_token = "your_token_here"
   ```
3. Update `FOLDER_PATH` and `FOLDER_PATH1` in `doodle.py` with your local image output directories

```bash
python doodle.py
```

Use the on-screen buttons to switch between Text and Drawing modes, Save intermediate frames, or Save & Exit to commit the note to Evernote.
