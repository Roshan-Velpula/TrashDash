import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from ultralytics import YOLO
import cv2
from obj_det import get_predicted_classes_with_boxes, gpt_items_model, gpt_model_detect_cats
from PIL import Image, ImageOps
import base64
from io import BytesIO

# Load environment variables
load_dotenv()
# Set page layout to wide
st.set_page_config(layout="wide")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

@st.cache_resource()
def load_model():
    """Retrieves the trained Yolo model and maps it to the CPU by default,
    can also specify GPU here."""
    model = YOLO(r'C:\Users\kingr\Downloads\M2 DSBA\advanced ai\TrashDetection\models\best_taco.pt')
    return model

def resize_image(image, size=(200, 200)):
    return image.resize(size)

def main():
    # Initialize session state
    if 'last_uploaded_bins' not in st.session_state:
        st.session_state.last_uploaded_bins = None
    if 'bins_image' not in st.session_state:
        st.session_state.bins_image = None
    if 'categories' not in st.session_state:
        st.session_state.categories = None
    # Display logo and title
    col1, col2 = st.columns([1, 10])
    with col1:
        st.image("logo.png", width=100)  # Adjust the width as needed
    with col2:
        st.title("TrashDash Vision")
    #st.title("TrashDash Vision")
    st.write("Upload an image or use the webcam to get detailed information about recyclable and non-recyclable objects.")

    model = load_model()

    # Sidebar for input method selection and bin detection
    with st.sidebar:
        st.header("Input Method")
        option = st.selectbox("Choose input method", ("Upload Image", "Webcam"))

        # Bin detection
        st.header("Detect Available Bins")
        uploaded_file_bins = st.file_uploader("Upload an image of the bins you have", type=["jpg", "jpeg", "png"])

        if uploaded_file_bins is not None:
            if uploaded_file_bins != st.session_state.last_uploaded_bins:
                st.session_state.last_uploaded_bins = uploaded_file_bins
                with open("temp_image_cats.jpg", "wb") as f:
                    f.write(uploaded_file_bins.getbuffer())
                
                st.session_state.bins_image = 'temp_image_cats.jpg'
                
                with st.spinner('Detecting bins...'):
                    cats = gpt_model_detect_cats(encode_image('temp_image_cats.jpg'), client)
                
                st.session_state.categories = cats['trashcans']
        else:
            st.session_state.categories = None
            st.session_state.bins_image = None
            
        if st.session_state.bins_image is not None:
            st.image(st.session_state.bins_image, caption='Available Bins')
            st.write(f"Detected Trash Cans: {st.session_state.categories}")
            
    # Main section for object detection
    if option == "Upload Image":
        uploaded_file = st.file_uploader("Choose an image of the object...", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            # Save uploaded image to a temporary file
            with open("temp_image.jpg", "wb") as f:
                f.write(uploaded_file.getbuffer())
            with st.sidebar:
                
                image = Image.open('temp_image.jpg').convert("RGB")
                
                st.image(resize_image(image), caption='Uploaded image')
            
            try:
                with st.spinner('Processing...'):
                    # Get predicted classes with bounding boxes
                    predictions = get_predicted_classes_with_boxes("temp_image.jpg", model, confidence_threshold=0.1)
                    
                    if predictions:
                        # Get AI classification
                        st.write("Detected objects and their recyclability information:")

                        image = Image.open('temp_image.jpg').convert("RGB")
                        image = ImageOps.exif_transpose(image)
                        for item in predictions:
                            for bounding_box in predictions[item]:
                                xmin, ymin, xmax, ymax = bounding_box
                                cropped_image = image.crop((xmin, ymin, xmax, ymax))
                                # Convert the cropped image to base64 string
                                resized_image = resize_image(cropped_image)
                                buffered = BytesIO()
                                cropped_image.save(buffered, format="JPEG")
                                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                                result = gpt_items_model(img_str, client, categories=st.session_state['categories'])
                                # Align image and text side by side
                                col1, col2 = st.columns([1, 3])
                                with col1:
                                    st.image(resized_image)
                                with col2:
                                    st.write(f"**Item:** {result['items'][0]['name']}")
                                    st.write(f"**Category:** {result['items'][0]['category']}")
                                    st.write(f"**Description:** {result['items'][0]['description']}")
                    else:
                        st.write("Routing to GPT vision")
                        baseimage = encode_image('temp_image.jpg')
                        result = gpt_items_model(baseimage, client, categories=st.session_state['categories'])
                        for item in result['items']:
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                st.image('temp_image.jpg')  # Adjust to display the appropriate image
                            with col2:
                                st.write(f"**Item:** {item['name']}")
                                st.write(f"**Category:** {item['category']}")
                                st.write(f"**Description:** {item['description']}")
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")

    elif option == "Webcam":
        # Initialize session state for webcam and capture handling
        if 'webcam_active' not in st.session_state:
            st.session_state.webcam_active = False
        if 'capture_image' not in st.session_state:
            st.session_state.capture_image = False

        col1, col2 = st.columns([1, 2])
        
        with col1:
            if st.button("Start Webcam"):
                st.session_state.webcam_active = True
                st.session_state.capture_image = False
            if st.button("Capture Image"):
                st.session_state.capture_image = True

        if st.session_state.webcam_active:
            cap = cv2.VideoCapture(0)
            stframe = st.empty()

            while st.session_state.webcam_active:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to capture image from webcam.")
                    break
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                stframe.image(frame_rgb, channels="RGB")

                if st.session_state.capture_image:
                    cv2.imwrite("temp_image.jpg", cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR))
                    st.session_state.webcam_active = False
                    cap.release()
                    break
        
        if os.path.exists("temp_image.jpg"):
            try:
                with st.spinner('Processing...'):
                    # Get predicted classes with bounding boxes
                    predictions = get_predicted_classes_with_boxes("temp_image.jpg", model, confidence_threshold=0.1)
                    
                    if predictions:
                        # Get AI classification
                        st.write("Detected objects and their recyclability information:")

                        image = Image.open('temp_image.jpg').convert("RGB")
                        image = ImageOps.exif_transpose(image)
                        for item in predictions:
                            for bounding_box in predictions[item]:
                                xmin, ymin, xmax, ymax = bounding_box
                                cropped_image = image.crop((xmin, ymin, xmax, ymax))
                                # Convert the cropped image to base64 string
                                resized_image = resize_image(cropped_image)
                                buffered = BytesIO()
                                cropped_image.save(buffered, format="JPEG")
                                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                                result = gpt_items_model(img_str, client, categories=st.session_state['categories'])
                                # Align image and text side by side
                                col1, col2 = st.columns([1, 3])
                                with col1:
                                    st.image(resized_image)
                                with col2:
                                    st.write(f"**Item:** {result['items'][0]['name']}")
                                    st.write(f"**Category:** {result['items'][0]['category']}")
                                    st.write(f"**Description:** {result['items'][0]['description']}")
                    else:
                        st.write("Routing to GPT vision")
                        baseimage = encode_image('temp_image.jpg')
                        result = gpt_items_model(baseimage, client, categories=st.session_state['categories'])
                        for item in result['items']:
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                st.image('temp_image.jpg')  # Adjust to display the appropriate image
                            with col2:
                                st.write(f"**Item:** {item['name']}")
                                st.write(f"**Category:** {item['category']}")
                                st.write(f"**Description:** {item['description']}")
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
