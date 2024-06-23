import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Define the date range
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 6, 15)
date_range = pd.date_range(start_date, end_date).to_pydatetime().tolist()

# Filter for weekdays only
weekday_dates = [date for date in date_range if date.weekday() < 5]

# Define the time peaks and distribution from 7H to 20H
def generate_peaked_time():
    peaks = [10.5, 12, 12.5, 13, 15.5, 18]  # Peak times: 10:30, 12:00, 12:30, 13:00, 15:30, 18:00
    weights = [2, 5, 5, 10, 3, 2]  # Weights for each peak
    peak_time = random.choices(peaks, weights=weights)[0]
    base_time = np.random.normal(loc=peak_time, scale=0.5)
    base_time = max(7, min(20, base_time))  # Ensure the time is within the 7 to 20 range
    hour = int(base_time)
    minute = int((base_time - hour) * 60)
    return f"{hour:02d}:{minute:02d}"

places = ['lobby', 'vending machine', 'par14', 'par13', 'par6']
items = ['paper cup', 'clear water bottle', 'drink can', 'wrapper', 'food', 'plastic film', 
         'paper', 'glass bottle', 'cardboard', 'coffee cup', 'banana peel', 'carton']
types = ['Plastic', 'Glass', 'Organic', 'Paper', 'Metal']
recyclability = ['Recyclable', 'non-recyclable', 'bio-degradable']
sorted_status_options = ['Sorted', 'Unsorted']

# Function to generate weights with one majority and others following a normal distribution
def generate_item_weights(majority_index, num_items, majority_weight=40, mean_weight=5, std_dev=2):
    weights = np.random.normal(loc=mean_weight, scale=std_dev, size=num_items).tolist()
    weights[majority_index] = majority_weight
    weights = [max(1, w) for w in weights]  # Ensure no weight is less than 1
    return weights

# Generate dummy data
num_records = 10000
data = []
for _ in range(num_records):
    date = random.choice(weekday_dates)
    time = generate_peaked_time()
    
    # Assign place with updated list
    place = random.choice(places)
    
    # Assign items with specific tracking locations and varied distribution
    if place == 'par13':
        weights = generate_item_weights(0, len(items))  # Majority paper cup
        item = random.choices(items, weights=weights)[0]
    elif place == 'vending machine':
        weights = generate_item_weights(1, len(items))  # Majority clear water bottle
        item = random.choices(items, weights=weights)[0]
    else:
        item = random.choices(items)[0]
        
    type_dict = {
        'paper cup': 'Paper',
        'clear water bottle': 'Plastic',
        'drink can': 'Metal',
        'wrapper': 'Plastic',
        'food': 'Organic',
        'plastic film': 'Plastic',
        'paper': 'Paper',
        'glass bottle': 'Glass',
        'cardboard': 'Paper',
        'coffee cup': 'Paper',
        'banana peel': 'Organic',
        'carton': 'Paper'
    }
    type = type_dict[item]
    recyc_dict = {
        'paper cup': 'Recyclable',
        'clear water bottle': 'Recyclable',
        'drink can': 'Recyclable',
        'wrapper': 'non-recyclable',
        'food': 'bio-degradable',
        'plastic film': 'non-recyclable',
        'paper': 'Recyclable',
        'glass bottle': 'Recyclable',
        'cardboard': 'Recyclable',
        'coffee cup': 'Recyclable',
        'banana peel': 'bio-degradable',
        'carton': 'Recyclable'
    }
    recyclability = recyc_dict[item]
    
    # Increase unsorted status for cafeteria
    if place == 'par13':
        sorted_status = random.choices(['Sorted', 'Unsorted'], weights=[10, 90])[0]
    else:
        sorted_status = random.choice(['Sorted', 'Unsorted'])
    
    data.append([
        date.strftime('%Y-%m-%d'), time, place, item, type, recyclability, sorted_status
    ])

# Create DataFrame
df = pd.DataFrame(data, columns=[
    'date', 'time', 'place', 'item', 'type', 'recyclability', 'sorted_status'
])

# Save to CSV
file_path = 'trash_detection_data.csv'
df.to_csv(file_path, index=False)
