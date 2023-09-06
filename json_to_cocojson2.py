import json
import os

# Directory paths
input_dir = "/Volumes/LaCie/OC_Finder_Annotations/DATE?_RAW_7500_MM_2/JSON"
output_dir = "/Volumes/LaCie/OC_Finder_Annotations/DATE?_RAW_7500_MM_2/COCOJSON"

# Image dimensions (assuming they are the same for all images)
image_height = 917
image_width = 1333

# Create a mapping of labels to category IDs
label_to_category_id = {
    "Background": 0,
    "Ghost": 1,
    "Unfused Monocyte": 2,
    "Small OC": 3,
    "Large OC": 4  # Added the new label and ID
}

# Function to calculate area using shoelace formula
def calculate_area(points):
    n = len(points)
    area = 0
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        area += (x1 * y2 - x2 * y1)
    return abs(area) / 2

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# List all JSON files in the input directory
json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]

# Initialize a variable to keep track of image IDs
current_image_id = 0

for json_file in json_files:
    # Load your existing JSON annotations
    input_path = os.path.join(input_dir, json_file)
    with open(input_path, 'r') as f:
        existing_annotations = json.load(f)

    # Increment the image ID for each new JSON file
    current_image_id += 1

    # Initialize the COCO format data structure
    coco_data = {
        "info": {},
        "licenses": [],
        "images": [],  # Updated images field
        "annotations": [],
        "categories": []
    }

    # Define a category ID mapping for your category labels
    category_id_mapping = {}

    # Iterate over your existing annotations and reformat them into the COCO structure
    for annotation in existing_annotations["shapes"]:
        # Extract relevant information from your existing annotations
        label = annotation["label"]
        points = annotation["points"]

        # Map the label to category_id using the label_to_category_id dictionary
        category_id = label_to_category_id.get(label, 0)

        # Calculate area using shoelace formula
        area = calculate_area(points)

        # Create the COCO annotation
        coco_annotation = {
            "id": len(coco_data["annotations"]) + 1,
            "image_id": current_image_id,  # Assign the current image ID
            "category_id": category_id,
            "segmentation": [points],
            "area": area,  # Assign the calculated area
            "bbox": [],  # Calculate the bounding box if available
            "iscrowd": 0
        }
        coco_data["annotations"].append(coco_annotation)

    # Populate the 'categories' field with category information
    for label, category_id in label_to_category_id.items():
        coco_category = {
            "id": category_id,
            "name": label,
            "supercategory": ""
        }
        coco_data["categories"].append(coco_category)

    # Populate the 'images' field with image information (once)
    coco_image = {
        "id": current_image_id,  # Assign the current image ID
        "width": image_width,
        "height": image_height,
        "file_name": "",  # Update with the image file name if available
    }
    coco_data["images"].append(coco_image)

    # Define the output JSON file name for COCO format
    output_file = json_file.replace('.json', '_coco.json')
    output_path = os.path.join(output_dir, output_file)

    # Save the COCO-formatted data to the output JSON file
    with open(output_path, 'w') as f:
        json.dump(coco_data, f)

    print(f"Converted {json_file} to COCO format and saved to {output_file}")

