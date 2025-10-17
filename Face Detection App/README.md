---
# Face Detection & Video Effects App - Professional 2025

  

A **real-time face detection and video effects application** built with **Python 3** and **PyQt5**.

This application detects people, applies live video effects, takes photos, and records videos via webcam in a professional and responsive interface.

  

---

  

## Features

  

-  **Real-time face detection** using OpenCV Haar Cascade

- Apply **Cartoon, Black & White, or Sepia effects**

- Adjustable **Sepia intensity** with slider

-  **Take photos**: snapshots saved automatically in `Photos/`

-  **Record videos**: save videos in `Videos/` folder with live recording notifications

- Responsive **PyQt5 GUI** with dark theme

- Supports multiple face detection simultaneously

- Professional and GitHub-ready code structure

  

---

  

## Demo

  

*Add GIFs or screenshots here to showcase the app.*

  

---

  

## Installation

  

1. **Clone this repository:**

  

```bash

git  clone  https://github.com/yourusername/FaceDetectionApp.git

cd  FaceDetectionApp
```

## Create a virtual environment (optional but recommended):

```
python  -m  venv  venv
```

# Linux/macOS

```source  venv/bin/activate```

# Windows

```venv\Scripts\activate```

## Install dependencies:

  


```pip  install  -r  requirements.txt```

Required  packages:  numpy,  opencv-python,  PyQt5

  

## Usage

Run  the  application:

```python  face_detection_app.py```

## Controls   
 
       Cartoon:  Apply  cartoon  effect


       Black & White:  Apply  grayscale  effect
   
 
       Sepia:  Apply  sepia  tone  effect
   
 
       Reset  Effect:  Remove  all  effects
   
 
       Take  Photo:  Capture  the  current  frame  in  Photos/
   
 
       Start/Stop  Video  Recording:  Record  webcam  video  in  Videos/
   
 
       Sepia  Intensity  Slider:  Adjust  sepia  effect  strength
   
 
       Messages  appear  for  face  detection,  photo  capture,  and  video     recording  status

## Project Structure

FaceDetectionApp/

│

├─ face_detection_app.py # Main Python app

├─ README.md # Project documentation

├─ requirements.txt # Dependencies

├─ Photos/ # Saved photos

└─ Videos/ # Saved videos

## License

This project is licensed under the MIT License. See LICENSE for details