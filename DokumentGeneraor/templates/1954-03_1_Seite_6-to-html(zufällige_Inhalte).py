from jinja2 import Environment, FileSystemLoader
from faker import Faker
from datetime import datetime
import random
import os
import json

fake = Faker('de_DE')

def format_date(value, format='%d.%m.%Y'):
    date_object = datetime.strptime(value, '%Y-%m-%d')
    return date_object.strftime(format)

script_dir = os.path.dirname(__file__)
output_dir = os.path.join(script_dir, 'fertigeHTML-Dokumente')
json_file_path = os.path.join(script_dir, '../../static/data', 'beschreibungen.json')

os.makedirs(output_dir, exist_ok=True)

with open(json_file_path, 'r', encoding='utf-8') as file:
    json_data = json.load(file)

# Generiert einen zufälligen Monat
def month_name(month_number):
    months = ["Januar", "Februar", "März", "April", "Mai", "Juni",
              "Juli", "August", "September", "Oktober", "November", "Dezember"]
    return months[month_number - 1]  # -1, da Listen in Python bei 0 beginnen


def generate_value_with_unit():
    units = json_data["einheiten"]
    value = random.randint(1, 1500)
    unit = random.choice(units)
    return {"value": value, "unit": unit}

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

# Gibt eine zufällige Beschreibung aus der JSON-Datei "ersteEbene" zurück
def get_random_beschreibung():
    beschreibungen = list(json_data["ersteEbene"].values())
    return random.choice(beschreibungen)

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
    'fake': fake,
    'gewicht': generate_value_with_unit(),
    'show_image_chance': random.randint(1, 100),
    'random_beschreibung': get_random_beschreibung(),
}

env = Environment(loader=FileSystemLoader(script_dir), trim_blocks=True, lstrip_blocks=True)
env.filters['format_date'] = format_date
env.filters['month_name'] = month_name
env.globals['get_random_beschreibung'] = get_random_beschreibung
template = env.get_template('1954-03_1_Seite_6-to-html(zufällige_Inhalte).html')
env.globals['generate_aufbau_description'] = generate_aufbau_description
env.globals['randint'] = random.randint
env.globals['fake'] = fake


output_html_path = os.path.join(output_dir, '1954-03_1_Seite_6-to-html(zufällige_Inhalte).html')
with open(output_html_path, 'w', encoding='utf-8') as file:
    file.write(template.render(daten))
