from jinja2 import Environment, FileSystemLoader
from faker import Faker
import random
import os
import json
import uuid
from collections import defaultdict

fake = Faker('de_DE')

# Konfigurationen
script_dir = os.path.dirname(__file__)  # Verzeichnis des aktuellen Skripts
output_dir = os.path.join(script_dir, 'fertigeHTML-Dokumente')  # Output-Verzeichnis
templates_dir = script_dir  # Annahme, dass Templates im selben Verzeichnis sind
json_file_path = os.path.join(script_dir, '../../static/data', 'beschreibungen.json')


os.makedirs(output_dir, exist_ok=True)

def load_json_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

json_data = load_json_data(json_file_path)

# Diese Struktur hält den aktuellen Zählerstand für jede Klasse
class_counter = defaultdict(int)

def get_next_class_id(class_name):
    # Inkrementiert den Zähler für die gegebene Klasse und gibt den Wert zurück
    class_counter[class_name] += 1
    return class_counter[class_name]

# Generiert eine Liste von 10 einzigartigen UUIDs
unique_ids = [str(uuid.uuid4()) for _ in range(10)]

# Erstellen einer Liste von Klassennamen
class_names = ["hauptueberschrift", "typueberschrift", "zwischenueberschrift", "artikelueberschrift"]


# Beispiel zur Generierung von einzigartigen IDs für jedes Element
unique_class_ids = {name: get_next_class_id(name) for name in class_names}

def generate_value_with_unit():
    units = json_data["einheiten"]
    value = random.randint(1, 1000)
    unit = random.choice(units)
    return f"{value} {unit}"

def generate_third_fourth_level():
    roman_numerals = ["I", "II"]
    third_level_count = random.randint(1, 2)
    third_level = {}
    display_mode = random.choice(["inline", "block"])
    for i in range(third_level_count):
        key = roman_numerals[i]
        value_with_unit = generate_value_with_unit()
        third_level[key] = {"value": value_with_unit, "display": display_mode}
    return third_level

def generate_second_level():
    zweite_ebene_keys = random.sample(list(json_data['zweiteEbene'].keys()), k=random.randint(2, 4))
    zweite_ebene = {json_data['zweiteEbene'][k]: generate_third_fourth_level() for k in zweite_ebene_keys}
    return zweite_ebene

def generate_first_level():
    erste_ebene_keys = random.sample(list(json_data['ersteEbene'].keys()), k=random.randint(3, 3))
    table_structure = {}
    for key in erste_ebene_keys:
        table_structure[json_data['ersteEbene'][key]] = generate_second_level()
    return table_structure



# Beispiel zur Generierung von einzigartigen IDs für jedes Element
unique_class_ids = {name: get_next_class_id(name) for name in class_names}

# Vorlage und Umgebung für Jinja2 einrichten
env = Environment(loader=FileSystemLoader(templates_dir),
                  trim_blocks=True,  # Entfernt den ersten Zeilenumbruch nach einem Block
                  lstrip_blocks=True)  # Entfernt führende Leerzeichen vor einem Block
template = env.get_template('gen2-to-html.html')

env.globals['randint'] = random.randint
env.globals['fake'] = fake
env.globals['get_next_class_id'] = get_next_class_id  # Hinzufügen der Funktion zu den Globals

stempel_nummer = random.randint(1, 90)
stempel_unten_mittig_nummer = random.randint(1, 49)

unique_class_numbers = list(range(1, 101))  # Erzeugt eine Liste von 1 bis 100

# Erstellen einer Liste von Klassennamen
class_names = ["hauptueberschrift", "typueberschrift", "zwischenueberschrift", "artikelueberschrift"]

# Beispiel zur Generierung von einzigartigen IDs für jedes Element
unique_class_ids = {name: i for i, name in enumerate(class_names)}

# Generierung von Beispielinhalten
daten = {
    'hauptueberschrift': fake.sentence(),
    'typueberschrift': fake.sentence(),
    'zwischenueberschrift': fake.sentence(),
    'artikelueberschrift': fake.sentence(),
    'artikel': fake.paragraphs(),
    'datum': fake.date(),
    'bildpfad': f"../../../static/images/stempel/stempel ({stempel_nummer}).png",
    'bildpfad_stempel_unten_mittig': f"../../../static/images/stempel/unten_mittig/stempel_unten_mittig ({stempel_unten_mittig_nummer}).png",
    'klammer_bildpfad': f"../../../static/images/bueroklammern/Klammer ({random.randint(1, 16)}).png",
    'table_data': generate_first_level(),
    'unique_class_ids': unique_class_ids,
    'fake': fake,
}

# Ausgabe des generierten HTML
output_html_path = os.path.join(output_dir, 'doc2.html')
with open(output_html_path, 'w', encoding='utf-8') as file:
    file.write(template.render(**daten))
