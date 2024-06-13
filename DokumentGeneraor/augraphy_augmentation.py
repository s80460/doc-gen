import augraphy
import cv2
import os
import time
from augraphy import *
from augraphy.augmentations import BindingsAndFasteners, BookBinding, BrightnessTexturize

# Originale Bilder ohne Degradierung
input_dir = "./DokumentGeneraor/output"

# Pfade zu Texturen
texture_path = "./static/images/paper_textures"

# Ausgabeordner für die degradierten Bilder
output_dir = "./DokumentGeneraor/output-augraphy"

# Sicherstellen, dass der Ausgabeordner existiert
os.makedirs(output_dir, exist_ok=True)

# Überprüfen, ob die Verzeichnisse korrekt sind
print(f"Input Directory: {os.path.abspath(input_dir)}")
print(f"Texture Path: {os.path.abspath(texture_path)}")
print(f"Output Directory: {os.path.abspath(output_dir)}")

#+-----------------------------------------------------------------------------------+#
#|                                       Effekte:                                    |#
#|  https://augraphy.readthedocs.io/en/latest/doc/source/list_of_augmentations.html  |#
#|                                                                                   |#
#|  Tipp: Manche Effekte verändern die Abmessungen des Bildes geringfügig.           |#
#|        Allerdings nicht mit den aktuellen Effekten in diesem Skript.              |#
#+-----------------------------------------------------------------------------------+#

# Definition der Augmentierungs-Phasen
ink_phase_augmentations = [
    InkBleed(intensity_range=(0.7, 1.0), p=0.8),
    SubtleNoise(p=0.7),
    BleedThrough(p=0.9),
    Dithering(p=0.1),
    OneOf([
        LowInkRandomLines(p=0.5),
        LowInkPeriodicLines(p=0.5)
    ], p=0.5),
]

paper_phase_augmentations = [
    PaperFactory(
        texture_path=texture_path,      # Setzt den Pfad zu den Texturen
        generate_texture=False,         # Keine neue Textur generieren
        generate_texture_background_type="gradient",     # Typ des Hintergrunds für die Textur, falls generiert
        generate_texture_edge_type="random",             # Art der Ränder für die Textur, falls generiert
        texture_enable_color=False,          # Texturfarbe ist deaktiviert
        blend_texture=True,                  # Mischen der Textur mit dem Papier
        blend_generate_texture=False,        # Keine neue Textur für das Mischen generieren
        blend_texture_path=texture_path,     # Pfad für die Textur beim Mischen
        blend_texture_background_type="random",   # Hintergrundtyp für die Textur beim Mischen
        blend_texture_edge_type="random",         # Randtyp für die Textur beim Mischen
        blend_method="ink_to_paper",              # Mischmethode, Tinte auf Papier
        p=1.0
    )
]

post_phase_augmentations = [
    Brightness(brightness_range=(0.90, 1.1), p=1.0),
    BindingsAndFasteners(
        overlay_types="darken",                      # Overlay-Art, hier wird verdunkelt
        effect_type="punch_holes",                   # Art des Effekts, hier Lochen
        width_range=(70, 80),                        # Bereich der Breite der Löcher
        height_range=(70, 80),                       # Bereich der Höhe der Löcher
        ntimes=(3, 3),                               # Anzahl der Löcher pro Reihe
        nscales=(1.5, 1.5),                          # Skalierungsfaktor für die Größe der Löcher
        edge="left",                                 # Positionierung der Löcher am linken Rand
        edge_offset=(30, 50),                        # Abstand der Löcher vom Rand
        p=0.5
    ),
    BrightnessTexturize(
        texturize_range=(0.8, 1.2), 
        deviation=0.03, 
        p=0.5
    ),
    ShadowCast(shadow_side='random',
        shadow_vertices_range=(1, 5),  # Bereich der Eckpunkte des Schattens, weniger Ecken für subtilere Schatten
        shadow_width_range=(0.1, 0.3),  # Breite des Schattens, schmaler für weniger dominante Schatten
        shadow_height_range=(0.1, 0.3),  # Höhe des Schattens, niedriger für weniger auffällige Schatten
        shadow_color=(160, 160, 160),         # Farbe des Schattens
        shadow_opacity_range=(0.2, 0.5),  # Opazität des Schattens, geringere Obergrenze für weniger Intensität
        shadow_iterations_range=(1, 1),  # Anzahl der Durchgänge, die der Schatteneffekt angewendet wird, weniger für subtilere Effekte
        shadow_blur_kernel_range=(60, 200),  # Größe des Weichzeichnungsfilters, kleinerer Bereich für weniger Blur
    p=1
    )
]

augmentation_pipeline = AugraphyPipeline(
    ink_phase=ink_phase_augmentations,
    paper_phase=paper_phase_augmentations,
    post_phase=post_phase_augmentations
)

# Liste aller PNG-Bilder im Input-Verzeichnis ausgeben
all_images = [entry.path for entry in os.scandir(input_dir) if entry.is_file() and entry.name.endswith('.png')]
# print(f"Gefundene Bilder: {all_images}")

# Durchlaufe alle PNG-Bilder im vorgegebenen Ordner, die nicht "bbox" im Namen haben
for image_path in all_images:
    if "bbox" in os.path.basename(image_path):
        # print(f"Überspringe Datei: {image_path}")
        continue
    
    print(f"Verarbeite Datei: {image_path}")
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print(f"Bild konnte nicht geladen werden: {image_path}")
        continue


#+------------------------------------------------------------------+#                                   
#|   Hier kann man einstellen, wie viele Exemplare des Bildes       |#
#|        generiert werden sollen (Data Augementation)              |#
#+------------------------------------------------------------------+#|                                                                                  |#

    for i in range(1):
        augmented_image = augmentation_pipeline(image)
        new_name = f"{os.path.splitext(os.path.basename(image_path))[0]}_{i}.png"
        output_image_path = os.path.join(output_dir, new_name)
        cv2.imwrite(output_image_path, augmented_image)
        print(f"Bild {i+1} wurde gespeichert unter: {output_image_path}")
