import cv2
import numpy as np
import requests
from PIL import Image
from io import BytesIO
#DISCLAIMER: ChatGPT helped me here. Thank you ChatGPT.
# Assuming cv2_image is your input image in BGR format
cv2_image = cv2.cvtColor(np.array(cam.raw_image), cv2.COLOR_RGB2BGR)

# Define lower and upper bounds for red color in HSV format
lower_red = np.array([0, 100, 100])  # Lower bound for hue, saturation, and value
upper_red = np.array([10, 255, 255])  # Upper bound for hue, saturation, and value

# Convert the image to HSV color space and create a mask to threshold the image for red color
hsv_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2HSV)
red_mask = cv2.inRange(hsv_image, lower_red, upper_red)

# Find contours in the red mask
contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Check if there are any contours (objects) in the red mask
if len(contours) > 0:
    # Find the largest contour based on its area
    largest_contour = max(contours, key=cv2.contourArea)
    
    # Calculate the area of the largest contour
    largest_contour_area = cv2.contourArea(largest_contour)

    # Set a threshold area for considering an object as red
    threshold_area = 10000  # You can adjust this threshold based on the object size you want to detect

    # Check if the largest object in the image is red based on the threshold area
    if largest_contour_area > threshold_area:
        result = "Yes"
    else:
        result = "No"
else:
    result = "No"

# Display the red object image
cam.show(red_mask)

# Send result to Airtable using their API
AIRTABLE_ENDPOINT = "https://api.airtable.com/v0/app742BjiRlmmPEao/Tasks"
AIRTABLE_API_KEY = "patRpTzy9QRwXTAl5.72ea248582c08626b98d88141a931c6b18029c6640b569f7e3b0f6d45025ed9b"

headers = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

data = {
  "records": [
    {
      "id": "rec7m8KXz6HG34mGp",
      "fields": {
        "Name": "Read Camera",
        "Color": result
      }
    }
  ]
      }

response = requests.patch(AIRTABLE_ENDPOINT, headers=headers, json=data)

print("Is there Red?: %s" % result)

if response.status_code == 200:
    print("Data sent to Airtable successfully!")
else:
    print(f"Failed to send data to Airtable. Status code: {response.status_code}")
