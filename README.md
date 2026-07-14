# Heart Anomaly Detection using AI

An AI-powered web application built with **Django** that detects potential heart anomalies from ECG images using a deep learning model.

The project combines machine learning with a user-friendly web interface, allowing users to upload ECG images and receive AI-based predictions.

> **Note:** This repository does **not** include the trained machine learning model due to file size and licensing considerations.

---

## Features

- Upload ECG images
- AI-based heart anomaly prediction
- Clean Django web interface
- Image preprocessing before prediction
- Responsive frontend
- Easy to integrate with your own trained model

---

## Technologies Used

- Python
- Django
- TensorFlow / Keras
- OpenCV
- NumPy
- Pillow
- HTML
- CSS
- JavaScript
- Bootstrap

---

## Project Structure

```
Heart-Anomaly-Detection/
│
├── app/
├── ecg_images/
├── media/
├── myproject/
├── static/
├── templates/
├── manage.py
├── requirements.txt
└── README.md
```

---

## Installation

### Clone the repository

```bash
git clone https://github.com/yourusername/heart-anomaly-detection.git
cd heart-anomaly-detection
```

### Create a virtual environment

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Django

Create your own `.env` file (or update `settings.py` depending on your project).

Example:

```env
SECRET_KEY=your-secret-key
DEBUG=True
```

---

## Machine Learning Model

The trained AI model is **not included** in this repository.

To run the project successfully, you must:

- Train your own heart anomaly detection model
- Or use an existing compatible TensorFlow/Keras model
- Place the model in the appropriate project directory
- Update the model path inside the Django project if necessary

For example:

```
model/
    heart_model.keras
```

or

```
model/
    heart_model.h5
```

Depending on your implementation.

---

## ▶ Running the Project

Apply migrations

```bash
python manage.py migrate
```

Start the development server

```bash
python manage.py runserver
```

Visit

```
http://127.0.0.1:8000/
```

---

## ⚠ Notes

This repository intentionally excludes:

- Trained AI model (.keras/.h5)
- Dataset
- Training notebooks
- Database
- Environment variables (.env)

These files should remain private or be generated locally.

---

## Future Improvements

- Improved prediction accuracy
- Multiple ECG classification
- Explainable AI visualizations
- User authentication
- Prediction history
- Cloud deployment

---

## License

This project is intended for educational and research purposes.

---

## Author

**Isha Akram**

BS Information Technology

Passionate about Artificial Intelligence, Machine Learning, and Full-Stack Web Development.

GitHub: https://github.com/akramisha
