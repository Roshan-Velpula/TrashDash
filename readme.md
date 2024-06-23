# TrashDash Vision

TrashDash Vision is an innovative application designed to help users identify recyclable and non-recyclable objects using AI-powered image recognition. This application leverages advanced AI models to analyze images and provide detailed information about the recyclability of various objects. Additionally, it can detect available trash bins from uploaded images, making waste management more efficient and environmentally friendly.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Main Page](#main-page)
  - [Dashboard](#dashboard)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)
- [License](#license)

## Introduction

In today's world, waste management is a critical issue. Properly sorting and recycling waste can significantly reduce environmental impact. However, identifying what can and cannot be recycled can be challenging. TrashDash Vision aims to simplify this process by using AI to analyze images of waste items and provide instant feedback on their recyclability. Additionally, the app can detect and categorize available trash bins from images, further aiding in effective waste management.

## Features

- **AI-Powered Object Detection**: Upload an image of an object, and the app will detect and classify it as recyclable or non-recyclable.
- **Trash Bin Detection**: Upload an image of your trash bins, and the app will identify and categorize them for easier sorting of waste.
- **Webcam Support**: Use your webcam to capture images of objects and receive real-time feedback.
- **Interactive Dashboard**: View detailed analytics and data visualizations related to waste management.

## Training

- Yolov8 model has been trained for segmentation and object detection task on TACO Dataset
- TACO Dataset is a publicly available annotated dataset for Trash Detection. [TACO Dataset](http://tacodataset.org/)

## Installation

To install and run TrashDash Vision, follow these steps:

1. **Clone the repository**:
    ```sh
    git clone https://github.com/Roshan-Velpula/TrashDash
    cd TrashDash
    ```

2. **Set up a virtual environment**:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    Create a `.env` file in the root directory and add your OpenAI API key:
    ```sh
    OPENAI_API_KEY=your_openai_api_key
    ```

## Usage

### Main Page

1. **Upload Image**: Select the "Upload Image" option from the sidebar to upload an image of an object. The app will analyze the image and provide detailed information about its recyclability.

2. **Webcam**: Select the "Webcam" option from the sidebar to capture an image using your webcam. The app will process the image and provide recyclability information.

3. **Detect Available Bins**: Upload an image of your trash bins in the sidebar. The app will identify and categorize the bins, making it easier to sort waste.

### Dashboard

1. **Navigation**: Click on the "Go to Dashboard" button in the sidebar to navigate to the dashboard page.
2. **View Analytics**: The dashboard provides detailed analytics and data visualizations related to waste management.

### Running the Application

1. **Start the Streamlit app**:
    ```sh
    streamlit run trash.py
    ```

2. **Access the application**: Open your web browser and go to `http://localhost:8501`.

## Technologies Used

- **Python**: The core programming language used for the application.
- **Streamlit**: A framework for creating interactive web applications.
- **OpenAI API**: Used for AI-powered image recognition and classification.
- **YOLO (You Only Look Once)**: A real-time object detection system.
- **Pillow**: Python Imaging Library for image processing.

