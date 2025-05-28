# Motion2Text ✍️➡️📝

Convert your hand gestures in the air to digital notes using AI! Motion2Text combines **OpenCV** for motion tracking, **Google Cloud Vision AI** for handwriting recognition, and the **Evernote API** for seamless note-taking.

## 🚀 Key Features
- **Air Writing Detection**: Track colored markers or objects in real-time using OpenCV
- **AI-Powered Text Conversion**: Leverage GCP's Vision AI to transcribe handwritten gestures
- **Smart Note Management**: Save results as text or images directly to Evernote
- **Customizable Workflow**: Choose between text notes or image uploads

## 🛠️ Tech Stack
| Component       | Technology Used | Purpose |
|----------------|----------------|---------|
| Motion Tracking | OpenCV (cv2) | Detects and traces colored objects in webcam feed |
| Text Recognition | Google Cloud Vision AI | Converts captured writing to digital text |
| Note Storage | Evernote API | Organizes transcriptions in your Evernote notebooks |

## ⚙️ How It Works
1. **Motion Capture**: The system tracks a specified colored object through your webcam
2. **Preprocessing**: Applies erosion/dilation to clean the input signal
3. **AI Conversion**: Captured gestures are sent to GCP Vision AI for handwriting recognition
4. **Note Creation**: Results are automatically saved to your Evernote account

## 📸 Demo
![Tracking Demo](https://user-images.githubusercontent.com/52961945/127783200-9f035f2d-4352-451a-95c8-3f44ab01800e.png)
*Real-time motion tracking*

![Evernote Output](https://user-images.githubusercontent.com/52961945/127783208-5ee2fa45-e4fa-462d-848e-222b902b23c7.png)
*Automatically created Evernote with transcribed text*

## 🔧 Setup
1. Install dependencies:
```bash
pip install opencv-python evernote3 google-cloud-vision
```

Configure your GCP Vision API credentials

Set up Evernote Developer Token

Run:

```bash
python motion2text.py
```

🤝 Contributing
Found a bug or have an enhancement idea? Open an issue or submit a PR!
