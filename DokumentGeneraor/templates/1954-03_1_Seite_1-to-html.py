from jinja2 import Environment, FileSystemLoader
from faker import Faker
from datetime import datetime, timedelta
import random
import os
import json
import uuid
from collections import defaultdict

fake = Faker('de_DE')

# Funktion zum Formatieren des Datums
def format_date(value, format='%d.%m.%Y'):
    date_object = datetime.strptime(value, '%Y-%m-%d')
    return date_object.strftime(format)


def random_date_filter(start_year, end_year):
    start_date = datetime.strptime(f'{start_year}-01-01', '%Y-%m-%d')
    end_date = datetime.strptime(f'{end_year}-12-31', '%Y-%m-%d')
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    random_date = start_date + timedelta(days=random_days)
    return random_date.strftime('%d.%m.%Y')


# Konfigurationen
script_dir = os.path.dirname(__file__)
output_dir = os.path.join(script_dir, 'fertigeHTML-Dokumente')
templates_dir = script_dir
json_file_path = os.path.join(script_dir, '../../static/data', 'beschreibungen.json')

# Stellen Sie sicher, dass die notwendigen Verzeichnisse existieren
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
    value = random.randint(1, 1500)
    unit = random.choice(units)
    return {"value": value, "unit": unit}

def generate_third_fourth_level(min_level=1, max_level=3):
    roman_numerals = ["I", "II", "III", "IV"]
    third_level_count = random.randint(min_level, max_level)
    third_level = {}
    display_mode = random.choice(["inline", "block"])
    for i in range(third_level_count):
        key = roman_numerals[i]
        value_with_unit = generate_value_with_unit()
        third_level[key] = {"value": value_with_unit, "display": display_mode}
    return third_level

def generate_second_level():
    alphabet = list("abcdefghijklmnopqrstuvwxyz")
    zweite_ebene_keys = random.sample(list(json_data['zweiteEbene'].keys()), k=random.randint(1, 6))
    zweite_ebene = {}
    for key in zweite_ebene_keys:
        for letter in alphabet:
            if letter not in zweite_ebene:
                zweite_ebene[letter] = generate_third_fourth_level()
                break
    return zweite_ebene


def generate_aufbau_description():
    dimension = random.choice(["Länge", "Breite", "Höhe", "Tiefe"])
    words = fake.words(nb=2, ext_word_list=[fake.lexify("???") for _ in range(100)])
    value = random.randint(220, 3500)
    unit = random.choice(["mm", "cm"])
    return f"{dimension} des Laderaumes {words[0]} {words[1]} {value} {unit}" 


def generate_table_data(num_letters):
    table_data = {}
    letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")[:num_letters]  

    for letter in letters:
        num_aufbauten = random.randint(2, 4)
        table_data[letter] = [None] * num_aufbauten

    return table_data



table_data = generate_table_data(random.randint(2, 2))

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
    'table_data': table_data,
}

# Vorlage und Umgebung für Jinja2 einrichten
env = Environment(loader=FileSystemLoader(templates_dir),
                  trim_blocks=True, 
                  lstrip_blocks=True)
env.filters['format_date'] = format_date
env.filters['random_date'] = random_date_filter
template = env.get_template('1954-03_1_Seite_1-to-html.html')

# Pass the function to the Jinja environment
env.globals['generate_aufbau_description'] = generate_aufbau_description
env.globals.update({
    'randint': random.randint,
    'fake': fake,
    'get_next_class_id': get_next_class_id
})
env.globals['random'] = random

# Ausgabe des generierten HTML
output_html_path = os.path.join(output_dir, '1954-03_1_Seite_1.html')
with open(output_html_path, 'w', encoding='utf-8') as file:
    file.write(template.render(daten))
