from PIL import Image, ImageDraw
import os

# Ordnerpfade anpassen
yolo_txt_folder_path = './DokumentGeneraor/bb-erfassen-output'
images_folder_path = './DokumentGeneraor/output'


"""
Gibt die Farbe für die gegebene Klassen-ID zurück.
Verwendet unterschiedliche Farben für verschiedene Objektklassen.
"""
def get_color_for_class(class_id):
    # Funktion zur Zuordnung von Farben zu Klassen basierend auf dem Identifier
    # (hier einen Standard entwickeln)
    class_id_to_color = {
        0: '#8B0000',  # hauptueberschrift
        1: '#008000',  # typueberschrift
        2: '#00008B',  # zwischenueberschrift
        3: '#8B008B',  # artikelueberschrift
        4: '#FF4500',  # artikel
        5: '#2F4F4F',  # companyname
        6: '#A0522D',  # sonder_Text
        7: '#DAA520',  # datum
        8: '#4682B4',  # stempelbild
        9: '#DEB887',  # pruefstelle
        10: '#5F9EA0', # Zusätzliche Klasse für Spezialfälle wie Tabellen
        11: '#9ACD32', # Zusätzliche Klasse für weitere spezielle Kennzeichnungen
        12: '#FF6347'  # Standardfarbe für nicht definierte Klassen-IDs
    }
    return class_id_to_color.get(class_id, '#000000')  # Standardfarbe Schwarz, falls keine Übereinstimmung gefunden wird


"""
Liest die Koordinaten aus einer YOLO-Textdatei und zeichnet entsprechende Boxen auf das Bild.
Speichert das bearbeitete Bild an einem angegebenen Ort.
"""

def draw_boxes_on_image_yolo(image_path, txt_file_path, output_image_path):
    if not os.path.exists(image_path):  # Überprüfen, ob die Bilddatei existiert
        print(f"Die Bilddatei {image_path} existiert nicht.")
        return

    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    image_width, image_height = image.size

    with open(txt_file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            class_id = int(parts[0])
            color = get_color_for_class(class_id)

            x_center_rel, y_center_rel, width_rel, height_rel = map(float, parts[1:5])
            x_center_abs = x_center_rel * image_width
            y_center_abs = y_center_rel * image_height
            width_abs = width_rel * image_width
            height_abs = height_rel * image_height

            x_min = x_center_abs - (width_abs / 2)
            y_min = y_center_abs - (height_abs / 2)
            x_max = x_center_abs + (width_abs / 2)
            y_max = y_center_abs + (height_abs / 2)

            draw.rectangle([x_min, y_min, x_max, y_max], outline=color, width=2)

    image.save(output_image_path)
    print(f'Bild gespeichert: {output_image_path}')

# Durchlaufe alle .txt-Dateien und zeichne die YOLO-Boxen
for file_name in os.listdir(yolo_txt_folder_path):
    if file_name.endswith('.txt') and 'bboxen' in file_name:
        base_name = file_name.replace('-bboxen.txt', '')
        image_file_name = f'{base_name}.png'
        image_path = os.path.join(images_folder_path, image_file_name)
        txt_file_path = os.path.join(yolo_txt_folder_path, file_name)
        output_image_path = os.path.join(images_folder_path, f'{base_name}_mitYOLO-bbox.png')

        draw_boxes_on_image_yolo(image_path, txt_file_path, output_image_path)
