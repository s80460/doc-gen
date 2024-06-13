import os
import subprocess

def clear_html_files(output_directory):
    # Überprüfe, ob das Verzeichnis existiert
    if os.path.exists(output_directory):
        # Liste aller Dateien im Verzeichnis
        files = os.listdir(output_directory)
        
        # Filtert die .html Dateien heraus und löscht sie
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(output_directory, file)
                os.remove(file_path)
                print(f"{file} wurde gelöscht.")

def execute_all_python_scripts_in_directory(directory):
    # Leere das Verzeichnis der fertigen HTML-Dokumente, bevor Skripte ausgeführt werden
    output_directory = os.path.join(directory, 'fertigeHTML-Dokumente')
    clear_html_files(output_directory)
    
    # Liste aller Dateien im Verzeichnis
    files = os.listdir(directory)
    
    # Filtert die .py Dateien heraus
    py_files = [file for file in files if file.endswith('.py')]

    for py_file in py_files:
        # Pfad zur Python-Datei
        py_file_path = os.path.join(directory, py_file)
        print(f"Ausführen: {py_file_path}")
        
        # Führt das Python-Skript aus
        try:
            subprocess.run(['python', py_file_path], check=True)
            print(f"{py_file} wurde erfolgreich ausgeführt.")
        except subprocess.CalledProcessError as e:
            print(f"Fehler beim Ausführen von {py_file}: {e}")

if __name__ == "__main__":
    # Bestimme das Verzeichnis des aktuellen Skripts
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Pfad zum Verzeichnis, in dem die Python-Dateien gespeichert sind, relativ zum aktuellen Skriptverzeichnis
    directory = os.path.join(current_dir, 'templates')
    execute_all_python_scripts_in_directory(directory)
