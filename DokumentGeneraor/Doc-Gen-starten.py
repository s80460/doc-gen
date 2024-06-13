import subprocess
import os

# ╔═╗╔═╗╔═════════════════════════════════════════════════════╗╔═╗╔═╗#
# ║ ║║ ║║                                                     ║║ ║║ ║#
# ║ ║║ ║║ ✨ Mit dieser Datei wird der Dokument-Generator ✨ ║║ ║║ ║#
# ║ ║║ ║║                     gestartet                       ║║ ║║ ║#
# ║ ║║ ║║                                                     ║║ ║║ ║#
# ╚═╝╚═╝╚═════════════════════════════════════════════════════╝╚═╝╚═╝#

def run_script(script_path):
    try:
        # Bestimmen, ob es sich um ein Python- oder JavaScript-Script handelt
        if script_path.endswith('.py'):
            command = ['python', script_path]
        elif script_path.endswith('.js'):
            command = ['node', script_path]
        else:
            print(f"Unsupported script type: {script_path}")
            return

        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
            print(f"Script {script_path} started...")
            # Diese Schleife sorgt dafür, dass die Ausgabe des gestarteten Skripts in Echtzeit in der Konsole angezeigt wird, während das Skript läuft
            while True:
                output = proc.stdout.readline()
                if output == '' and proc.poll() is not None:
                    break
                if output:
                    print(output.strip())
            proc.wait()  # Warten auf das Ende des Prozesses
            print(f"Script {script_path} finished with exit code {proc.returncode}")
    except Exception as e:
        print(f"Error running script {script_path}: {e}")

if __name__ == "__main__":
    # Bestimmt den Pfad zum Projekt-Root und den Pfad zum Skript-Verzeichnis
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    script_dir = os.path.join(project_root, 'DokumentGeneraor')

    # Setze die relativen Pfade zu den Skripten
    scripts = [
        'alleTemplatesGenerieren.py', # Die zu jedem Template gehörigen Python-Dateien wandeln alle jinja-html-Dateien in statische html-Datei um
        'html-to-png+bb-analyse.js', # Die statischen html-Dateien in PNG-Dateien umwandeln und die Bounding-Boxes analysieren
        'alle-JSON-bb-zeichnen.py', # Die Bounding-Boxes werden in die PNG-Dateien gezeichnet
        'alle-JSON-to-YOLO.py', # Die JSON-Koordinaten der Bounding-Boxes werden in das YOLO-Format umgewandelt
        'alle-YOLO-bb-zeichnen.py', # Die YOLO-Koordinaten der Bounding-Boxes werden in die PNG-Dateien gezeichnet
        'augraphy_augmentation.py', # Die Bilder werden augmentiert bzw. degradiert
    ]

    for script in scripts:
        script_path = os.path.join(script_dir, script)
        run_script(script_path)
