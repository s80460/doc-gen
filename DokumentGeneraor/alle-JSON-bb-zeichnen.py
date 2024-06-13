from PIL import Image, ImageDraw
import json
import os

# Pfad zum Ordner, der die JSON-Bounding-Box-Koordinaten enthält
json_folder_path = './DokumentGeneraor/bb-erfassen-output'

# Pfad zum Ordner, der die Bildausgaben speichert
images_folder_path = './DokumentGeneraor/output'

# Definition der A4-Abmessungen in Pixel bei 300 DPI
A4_WIDTH = 2480
A4_HEIGHT = 3508

# Skalierungsfaktor, um die Größe von Elementen anzupassen
SCALE_FACTOR = 2.0

def draw_bounding_boxes(input_image_path, boxes, output_image_path):
    """Verarbeitet ein Bild, indem es Bounding-Boxen basierend auf den JSON-Daten zeichnet."""
    try:
        image = Image.open(input_image_path)
    except FileNotFoundError:
        print(f"Bild {input_image_path} nicht gefunden.")
        return

    draw = ImageDraw.Draw(image)  # Erstelle ein Zeichenobjekt
    for box in boxes:
        # Ignoriere Bounding-Boxen mit leerem Text, es sei denn, es handelt sich um Bilder
        if box['text'].strip() == "" and box['identifier'] != "image":
            continue

        # Skaliert die Koordinaten und Größe der Bounding-Boxen
        scaled_x = box['x'] * SCALE_FACTOR
        scaled_y = box['y'] * SCALE_FACTOR
        scaled_width = box['width'] * SCALE_FACTOR
        scaled_height = box['height'] * SCALE_FACTOR

        # Farbe für die Bounding-Box abhängig von der Klassifizierung wählen
        color = get_color_for_class(box['identifier'])
        draw.rectangle([scaled_x, scaled_y, scaled_x + scaled_width, scaled_y + scaled_height], outline=color, width=3)

    image.save(output_image_path)  # Speichert das bearbeitete Bild
    print(f"Bild erfolgreich gespeichert unter: {output_image_path}")

    # Funktion zur Zuordnung von Farben zu Klassen basierend auf dem Identifier
    # (hier einen Standard entwickeln)
def get_color_for_class(identifier):
    if identifier.startswith('hauptueberschrift_'):
        color = '#CD5C5C'
    elif identifier.startswith('typueberschrift_'):
        color = '#3CB371'
    elif identifier.startswith('zwischenueberschrift_'):
        color = '#4682B4'
    elif identifier.startswith('artikelueberschrift_'):
        color = '#DAA520'
    elif identifier.startswith('artikel_'):
        color = '#6495ED'
    elif identifier == 'companyname':
        color = '#FF6347'
    elif identifier == 'sonder_Text':
        color = '#FFD700'
    elif identifier.startswith('valueunit'):
        color = '#98FB98'
    elif identifier.startswith('datum_'):
        color = '#6A5ACD'
    elif 'level' in identifier or 'td_' in identifier or 'th_' in identifier or 'table_' in identifier or 'tabelle_' in identifier:
        color = '#DEB887'
    elif identifier.startswith('stempelbild_'):
        color = '#808080'
    else:
        color = '#B0C4DE'
    return color

# Durchlaufen aller JSON-Dateien im Verzeichnis
for file_name in os.listdir(json_folder_path):
    if file_name.endswith('.json'):
        json_path = os.path.join(json_folder_path, file_name)
        base_name = file_name.rsplit('-', 1)[0]  # Extrahiere den Basisnamen des Bildes
        image_path = os.path.join(images_folder_path, f'{base_name}.png')
        output_image_path = os.path.join(images_folder_path, f'{base_name}_mit_JSON-bbox.png')
        with open(json_path, 'r') as f:
            boxes = json.load(f)  # Lade JSON-Daten
        draw_bounding_boxes(image_path, boxes, output_image_path)
