import sys
import os
import cv2
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QSlider, QSizePolicy
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# -----------------------------
# Camera Thread for real-time capture
# -----------------------------
class CameraThread(QThread):
    frame_updated = pyqtSignal(np.ndarray)
    faces_detected = pyqtSignal(int)
    message_signal = pyqtSignal(str, str)  # message, color

    def __init__(self):
        super().__init__()
        self._running = True
        self.cap = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.effect = None
        self.sepia_intensity = 1.0

    def run(self):
        while self._running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            self.faces_detected.emit(len(faces))

            display_frame = frame.copy()

            # Apply effects
            if self.effect == "cartoon":
                gray_blur = cv2.medianBlur(gray, 5)
                edges = cv2.adaptiveThreshold(
                    gray_blur, 255,
                    cv2.ADAPTIVE_THRESH_MEAN_C,
                    cv2.THRESH_BINARY, 9, 9
                )
                color = cv2.bilateralFilter(display_frame, 9, 300, 300)
                display_frame = cv2.bitwise_and(color, color, mask=edges)
            elif self.effect == "bw":
                display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2GRAY)
                display_frame = cv2.cvtColor(display_frame, cv2.COLOR_GRAY2BGR)
            elif self.effect == "sepia":
                sepia_kernel = np.array([
                    [0.272, 0.534, 0.131],
                    [0.349, 0.686, 0.168],
                    [0.393, 0.769, 0.189]
                ])
                display_frame = cv2.transform(display_frame, sepia_kernel)
                display_frame = np.clip(display_frame * self.sepia_intensity, 0, 255).astype(np.uint8)

            self.frame_updated.emit(display_frame)

        self.cap.release()

    def stop(self):
        self._running = False
        self.wait()


# -----------------------------
# Main Application
# -----------------------------
class FaceDetectionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Detection - Professional 2025")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

        # Video display label
        self.video_label = QLabel(self)
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_label.setAlignment(Qt.AlignCenter)

        # Message label
        self.msg_label = QLabel("No person detected", self)
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.msg_label.setStyleSheet("font-size: 18px;")

        # Buttons
        self.cartoon_btn = QPushButton("Cartoon")
        self.bw_btn = QPushButton("Black & White")
        self.sepia_btn = QPushButton("Sepia")
        self.reset_btn = QPushButton("Reset Effect")
        self.photo_btn = QPushButton("Take Photo")
        self.video_btn = QPushButton("Start/Stop Video Recording")

        # Sepia intensity slider
        self.sepia_slider = QSlider(Qt.Horizontal)
        self.sepia_slider.setMinimum(1)
        self.sepia_slider.setMaximum(100)
        self.sepia_slider.setValue(100)

        # Layout setup
        v_layout = QVBoxLayout()
        v_layout.addWidget(self.video_label)
        v_layout.addWidget(self.msg_label)
        h_layout = QHBoxLayout()
        for btn in [self.cartoon_btn, self.bw_btn, self.sepia_btn, self.reset_btn,
                    self.photo_btn, self.video_btn]:
            h_layout.addWidget(btn)
        v_layout.addLayout(h_layout)
        v_layout.addWidget(QLabel("Sepia Intensity"))
        v_layout.addWidget(self.sepia_slider)
        self.setLayout(v_layout)

        # Initialize camera thread
        self.thread = CameraThread()
        self.thread.frame_updated.connect(self.update_frame)
        self.thread.faces_detected.connect(self.update_face_count)
        self.thread.start()

        # Connect buttons
        self.cartoon_btn.clicked.connect(lambda: self.set_effect("cartoon"))
        self.bw_btn.clicked.connect(lambda: self.set_effect("bw"))
        self.sepia_btn.clicked.connect(lambda: self.set_effect("sepia"))
        self.reset_btn.clicked.connect(lambda: self.set_effect(None))
        self.photo_btn.clicked.connect(self.capture_photo)
        self.video_btn.clicked.connect(self.toggle_video_recording)
        self.sepia_slider.valueChanged.connect(self.update_sepia_intensity)

        # Video recording
        self.recording = False
        self.video_writer = None

        # Last captured frame
        self.current_frame = None

    def set_effect(self, effect_name):
        self.thread.effect = effect_name
        self.msg_label.setText(f"{effect_name.upper()} effect active!" if effect_name else "Effect reset")

    def update_sepia_intensity(self):
        self.thread.sepia_intensity = self.sepia_slider.value() / 100

    def closeEvent(self, event):
        if self.recording:
            self.stop_video_recording()
        self.thread.stop()
        event.accept()

    def update_frame(self, cv_img):
        self.current_frame = cv_img.copy()
        qt_img = self.convert_cv_to_qt(cv_img)
        self.video_label.setPixmap(qt_img)

        if self.recording and self.video_writer is not None:
            self.video_writer.write(cv2.cvtColor(cv_img, cv2.COLOR_RGB2BGR))

    def update_face_count(self, count):
        if count > 0:
            self.msg_label.setText(f"✅ {count} person(s) detected!")
        else:
            self.msg_label.setText("No person detected")

    def convert_cv_to_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(qt_image.scaled(
            self.video_label.width(), self.video_label.height(), Qt.KeepAspectRatio))

    def capture_photo(self):
        if self.current_frame is not None:
            os.makedirs("Photos", exist_ok=True)
            filename = datetime.now().strftime("Photos/photo_%Y%m%d_%H%M%S.png")
            cv2.imwrite(filename, cv2.cvtColor(self.current_frame, cv2.COLOR_RGB2BGR))
            self.msg_label.setText("📸 Photo saved!")
            os.startfile(os.path.abspath("Photos"))

    def toggle_video_recording(self):
        if not self.recording:
            if self.current_frame is not None:
                os.makedirs("Videos", exist_ok=True)
                filename = datetime.now().strftime("Videos/video_%Y%m%d_%H%M%S.avi")
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                h, w, _ = self.current_frame.shape
                self.video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (w, h))
                self.recording = True
                self.msg_label.setText("🎥 Video recording started")
                self.msg_label.setStyleSheet("color: #00FF00; font-size: 18px;")
        else:
            self.stop_video_recording()

    def stop_video_recording(self):
        self.recording = False
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
            self.msg_label.setText("🎥 Video recording stopped")
            self.msg_label.setStyleSheet("color: #FF0000; font-size: 18px;")
            os.startfile(os.path.abspath("Videos"))


# -----------------------------
# Application entry point
# -----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceDetectionApp()
    window.show()
    sys.exit(app.exec_())
