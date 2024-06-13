import json
import os

# Verzeichnispfade anpassen
json_folder_path = './DokumentGeneraor/bb-erfassen-output'

# Mapping von `identifier`-Präfixen zu Klassen-IDs mit den neuen Identifikatoren
identifier_to_class_id = {
    'hauptueberschrift': 0,
    'typueberschrift': 1,
    'zwischenueberschrift': 2,
    'artikelueberschrift': 3,
    'artikel': 4,
    'companyname': 5,
    'sonder_Text': 6,
    'datum': 7,
    'stempelbild': 8,
    'pruefstelle': 9,

}

# Bildgrößen anpassen
image_size = (2483/2, 3512/2)  # Annahme der Zielbildgröße als die Hälfte der Originalgröße

def convert_boxes_to_yolo_format(boxes, img_size):
    yolo_boxes = []
    for box in boxes:
        x_center = (box['x'] + box['width'] / 2) / img_size[0]
        y_center = (box['y'] + box['height'] / 2) / img_size[1]
        width = box['width'] / img_size[0]
        height = box['height'] / img_size[1]

        identifier_prefix = box['identifier'].split('_')[0]
        class_id = 12  # Standardwert für nicht definierte Identifiers

        # Spezifische Klassenzuweisungen für komplexe Identifiers
        if any(keyword in box['identifier'] for keyword in ['level', 'table', 'Tabelle', 'value', 'unit']):
            class_id = 10
        elif any(keyword in box['identifier'] for keyword in ['img', 'Stempel', 'klammer']):
            class_id = 11
        else:
            for prefix, id in identifier_to_class_id.items():
                if prefix in box['identifier']:
                    class_id = id
                    break

        yolo_format = f"{class_id} {x_center} {y_center} {width} {height}"
        yolo_boxes.append(yolo_format)

    return yolo_boxes

# Iteriere durch alle JSON-Dateien im angegebenen Verzeichnis
for file_name in os.listdir(json_folder_path):
    if file_name.endswith('.json'):
        json_path = os.path.join(json_folder_path, file_name)
        output_yolo_path = json_path.replace('.json', '.txt')

        # Lade JSON-Daten
        with open(json_path, 'r') as file:
            boxes = json.load(file)

        # Konvertiere die Daten und speichere sie
        yolo_boxes = convert_boxes_to_yolo_format(boxes, image_size)
        with open(output_yolo_path, 'w') as yolo_file:
            for box in yolo_boxes:
                yolo_file.write(box + "\n")

        print(f"YOLO-Koordinaten wurden erfolgreich in {output_yolo_path} gespeichert.")
