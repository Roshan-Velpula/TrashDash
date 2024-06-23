import argparse
from prompts import custom_answer_prompt_template, gpt_vis, prompt_items, categorize, prompt_cats
import json
from PIL import Image, ImageOps
import base64
from io import BytesIO



def get_predicted_classes_with_boxes(image_path, model, confidence_threshold=0.3):
    results = model(image_path)
    predicted_classes = {}

    for result in results:  # Iterate through detection results
        for box in result.boxes:  # Iterate through bounding boxes
            if box.conf.item() > confidence_threshold:  # Check confidence level
                class_id = int(box.cls.item())
                class_name = model.names[class_id]  # Get class name from class ID
                bounding_box = [int(box.xyxy[0][i].item()) for i in range(4)]  # Convert tensor to list of ints
                if class_name in predicted_classes:
                    predicted_classes[class_name].append(bounding_box)
                else:
                    predicted_classes[class_name] = [bounding_box]

    return predicted_classes



def get_ai_class(predicted_classes, client):
    
    items_list = list(predicted_classes.keys())
    
    answer_prompt = f"""
            {custom_answer_prompt_template}
            items: {items_list}
                """
    
    response = client.chat.completions.create(
            model="gpt-4o",
            response_format = {'type': 'json_object'},
            messages=[
                {"role": "system", "content": "Only output valid JSON"},
                {"role": "user", "content": answer_prompt}
            ],
            
            )
    
    return json.loads(response.choices[0].message.content)

def gpt_model_detect_cats(baseimage, client):
    
    response = client.chat.completions.create(
    model="gpt-4o",
    response_format = {'type': 'json_object'},
    messages=[
        {"role": "system", "content": f"{categorize}"},
        {"role": "user", "content": [
            {"type": "text", "text": f"{prompt_cats}"},
            {"type": "image_url", "image_url": {
                "url": f"data:image/png;base64,{baseimage}"}
            }
        ]}
    ],
    temperature=0.0,
    )
    
    return json.loads(response.choices[0].message.content)


def gpt_items_model(baseimage, client, categories = None):
    
    if categories:
        cats = categories
    else:
        cats = 'Yellow, Green, Grey, Brown'
    response = client.chat.completions.create(
    model="gpt-4o",
    response_format = {'type': 'json_object'},
    messages=[
        {"role": "system", "content": f"{gpt_vis}"},
        {"role": "user", "content": [
            {"type": "text", "text": f"{prompt_items} \n Categories: {cats}"},
            {"type": "image_url", "image_url": {
                "url": f"data:image/png;base64,{baseimage}"}
            }
        ]}
    ],
    temperature=0.0,
    )
    
    return json.loads(response.choices[0].message.content)


def get_objects(image_path, predicted_classes, gpt_items_model_cats, client, categories=None):
    
    image = Image.open(image_path).convert("RGB")
    image = ImageOps.exif_transpose(image)
    detects = []
    for item in predicted_classes:
        for bounding_box in predicted_classes[item]:
            xmin, ymin, xmax, ymax = bounding_box
            cropped_image = image.crop((xmin, ymin, xmax, ymax))
                
                # Convert the cropped image to base64 string
            buffered = BytesIO()
            cropped_image.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            result = gpt_items_model_cats(img_str, client, categories)
            result['image'] = img_str
            
            detects.append(result)
    return detects
            
    
    


def crop_and_return_items(image_path, predicted_classes, data):
    image = Image.open(image_path).convert("RGB")
    image = ImageOps.exif_transpose(image)  # Correct image orientation
    
    result = {"items": []}
    
    for item in data['items']:
        item_name = item['name']
        if item_name in predicted_classes:
            for bounding_box in predicted_classes[item_name]:
                # Crop the image with the bounding box
                xmin, ymin, xmax, ymax = bounding_box
                cropped_image = image.crop((xmin, ymin, xmax, ymax))
                
                # Convert the cropped image to base64 string
                buffered = BytesIO()
                cropped_image.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                
                # Add the image to the item
                new_item = item.copy()
                new_item["image"] = img_str
                result["items"].append(new_item)
        else:
            print(f"No predictions for {item_name}")
    
    return result

def display_image_from_base64(base64_str):
    # Decode the base64 string
    img_data = base64.b64decode(base64_str)
    # Convert the binary data to a PIL Image
    img = Image.open(BytesIO(img_data))
    return img



def gpt_model_detect_cats(baseimage, client):
    
    response = client.chat.completions.create(
    model="gpt-4o",
    response_format = {'type': 'json_object'},
    messages=[
        {"role": "system", "content": f"{categorize}"},
        {"role": "user", "content": [
            {"type": "text", "text": f"{prompt_cats}"},
            {"type": "image_url", "image_url": {
                "url": f"data:image/png;base64,{baseimage}"}
            }
        ]}
    ],
    temperature=0.0,
    )
    
    return json.loads(response.choices[0].message.content)