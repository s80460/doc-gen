from jinja2 import Environment, FileSystemLoader
from faker import Faker
import random
import os
import json
import uuid
from collections import defaultdict

fake = Faker('de_DE')

# Konfigurationen
script_dir = os.path.dirname(__file__)
output_dir = os.path.join(script_dir, 'fertigeHTML-Dokumente')
templates_dir = script_dir
json_file_path = os.path.join(script_dir, '../../static/data', 'beschreibungen.json')


os.makedirs(output_dir, exist_ok=True)

def load_json_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

json_data = load_json_data(json_file_path)

# Diese Struktur hält den aktuellen Zählerstand für jede Klasse
class_counter = defaultdict(int)

def get_next_class_id(class_name):
    class_counter[class_name] += 1
    return class_counter[class_name]

def generate_value_with_unit():
    units = json_data["einheiten"]
    value = random.randint(1, 1000)
    unit = random.choice(units)
    return f"{value} {unit}"

def generate_third_fourth_level():
    roman_numerals = ["I", "II", "III", "IV"]  # Erweiterte Liste der römischen Ziffern
    third_level_count = random.randint(3, 4)  # Jetzt können bis zu 4 Ebenen generiert werden
    third_level = {}
    display_mode = random.choice(["inline", "block"])
    for i in range(third_level_count):
        key = roman_numerals[i]
        value_with_unit = generate_value_with_unit()
        third_level[key] = {"value": value_with_unit, "display": display_mode}
    return third_level

def generate_second_level():
    zweite_ebene_keys = random.sample(list(json_data['zweiteEbene'].keys()), k=random.randint(1, 2))
    zweite_ebene = {key: generate_third_fourth_level() for key in zweite_ebene_keys}
    return zweite_ebene

def generate_first_level():
    erste_ebene_keys = random.sample(list(json_data['ersteEbene'].keys()), k=random.randint(6, 7))
    table_structure = {json_data['ersteEbene'][key]: generate_second_level() for key in erste_ebene_keys}
    return table_structure

table_data = generate_first_level()

daten = {
    'hauptueberschrift': fake.sentence(),
    'typueberschrift': fake.sentence(),
    'zwischenueberschrift': fake.sentence(),
    'artikelueberschrift': fake.sentence(),
    'artikel': fake.paragraphs(nb=3),
    'datum': fake.date(),
    'bildpfad': f"../../../static/images/stempel/stempel ({random.randint(1, 90)}).png",
    'bildpfad_stempel_unten_mittig': f"../../../static/images/stempel/unten_mittig/stempel_unten_mittig ({random.randint(1, 49)}).png",
    'klammer_bildpfad': f"../../../static/images/bueroklammern/Klammer ({random.randint(1, 16)}).png",
    'table_data': table_data,
    'unique_class_ids': {name: get_next_class_id(name) for name in ["hauptueberschrift", "typueberschrift", "zwischenueberschrift", "artikelueberschrift"]},
    'fake': fake,
    'zweiteEbene': json_data['zweiteEbene'],
}

# Vorlage und Umgebung für Jinja2 einrichten
env = Environment(loader=FileSystemLoader(templates_dir))
template = env.get_template('gen5-to-html.html')

env.globals.update({
    'randint': random.randint,
    'fake': fake,
    'get_next_class_id': get_next_class_id
})

# Ausgabe des generierten HTML
output_html_path = os.path.join(output_dir, 'doc5.html')
with open(output_html_path, 'w', encoding='utf-8') as file:
    file.write(template.render(daten))
