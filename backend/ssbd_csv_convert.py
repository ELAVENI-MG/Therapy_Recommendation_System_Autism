import os
import xml.etree.ElementTree as ET
import pandas as pd

# Folder containing XML files
ANNOTATION_FOLDER = "C:/Users/acer/Downloads/Annotations/Annotations"   # change path

data = []

def parse_duration(duration_str):
    # convert "26s" → 26
    return int(duration_str.replace("s", "").strip())

for file in os.listdir(ANNOTATION_FOLDER):
    if file.endswith(".xml"):
        file_path = os.path.join(ANNOTATION_FOLDER, file)

        tree = ET.parse(file_path)
        root = tree.getroot()

        video_id = root.attrib.get("id")
        keyword = root.attrib.get("keyword")

        frames = int(root.find("frames").text)
        duration = parse_duration(root.find("duration").text)

        behaviours = root.find("behaviours")
        behaviour_count = int(behaviours.attrib.get("count"))

        for behaviour in behaviours.findall("behaviour"):
            bodypart = behaviour.find("bodypart").text
            category = behaviour.find("category").text
            intensity = behaviour.find("intensity").text

            data.append([
                video_id,
                keyword,
                frames,
                duration,
                bodypart,
                category,
                intensity,
                behaviour_count
            ])

# Create DataFrame
columns = [
    "video_id",
    "keyword",
    "frames",
    "duration",
    "bodypart",
    "category",
    "intensity",
    "behaviour_count"
]

df = pd.DataFrame(data, columns=columns)

# Save CSV
df.to_csv("ssbd_dataset.csv", index=False)

print("✅ CSV file created successfully!")
print(df.head())