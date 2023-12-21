import streamlit as st
import subprocess
import datetime
import pandas as pd 
import os

def execute_command(command_description, command, stream_output=True):
    try:
        # Verwenden von HTML zum Hervorheben in grüner Farbe und Fettdruck
        st.markdown(f'<span style="color: green; font-weight: bold;">{command_description}</span>', unsafe_allow_html=True)
        if stream_output:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            while True:
                output = process.stdout.readline()
                if "[DEBUG]" in output:  # Überspringe Zeilen mit "[DEBUG]"
                    continue
                if output == '' and process.poll() is not None:
                    break
                if output:
                    st.write(output.strip())
        else:
            subprocess.call(command)
    except Exception as e:
        st.write(f"Error: {str(e)}")


def run_script(QuPathApp, WSIdir, OPSCCdir, ProjectDir):
    commands = [
        ("STEP 1/9: Building QuPath project.", ['python', f"{OPSCCdir}/Python_scripts/CreateQuPathProject.py", '-i', WSIdir, '-p', ProjectDir]),
        ("STEP 2/9: Exporting tissue tiles for segmentation.", [QuPathApp, '--quiet', '--log', 'OFF', 'script', f"{OPSCCdir}/QuPathscripts/Export_tiles_annotation_after_tissue_detection_tile_exporter_final.groovy", '--project', f"{ProjectDir}/project.qpproj", '--args', OPSCCdir]),
        ("STEP 3/9: Running segmentation of viable tumor areas.", ['python', f"{OPSCCdir}/Python_scripts/Segmentation.py"]),
        ("STEP 4/9: Importing masks into QuPath.", [QuPathApp, '--quiet', '--log', 'OFF', 'script', f"{OPSCCdir}/QuPathscripts/import_binary_masks.groovy", '--project', f"{ProjectDir}/project.qpproj"]),
        ("STEP 5/9: Exporting tumor tiles.", [QuPathApp, '--quiet', '--log', 'OFF', 'script', f"{OPSCCdir}/QuPathscripts/Export_tiles_annotation_tile_exporter.groovy", '--project', f"{ProjectDir}/project.qpproj"]),
        ("STEP 6/9: Stain normalization of tumor tiles.", ['python', f"{OPSCCdir}/Python_scripts/StainNormalization.py"]),
        ("STEP 7/9: Classifying tumor tiles for HPV-association.", ['python', '-W', 'ignore::UserWarning:keras.engine.training:2035', f"{OPSCCdir}/Python_scripts/Classification.py"]),
        ("STEP 8/9: Visualizing results and saving them into QuPath project.", [QuPathApp, '--quiet', '--log', 'OFF', 'script', f"{OPSCCdir}/QuPathscripts/Visualize_tiles_directory.groovy", '--project', f"{ProjectDir}/project.qpproj"]),
        ("STEP 9/9: Rendering results.", [QuPathApp, '--quiet', '--log', 'OFF', 'script', f"{OPSCCdir}/QuPathscripts/Export_render_image_no_viewer.groovy", '--project', f"{ProjectDir}/project.qpproj"])
    ]

    # Fortschrittsbalken initialisieren
    progress_bar = st.progress(0)
    total_commands = len(commands)

    for idx, (desc, cmd) in enumerate(commands):
        execute_command(desc, cmd)
        
        # Update Fortschrittsbalken
        progress_percentage = (idx + 1) / total_commands
        progress_bar.progress(progress_percentage)


    
def open_image_in_qupath(QuPathApp, ProjectDir, display_name):
    # Erstellen Sie den Befehl, um das Bild in QuPath zu öffnen
    command = [
        QuPathApp,
        '--project', 
        f"{ProjectDir}/project.qpproj",
        '--image',
        display_name
    ]
    # Verwenden Sie Ihre `execute_command`-Funktion, um den Befehl auszuführen
    execute_command(f"Opening {display_name} in QuPath", command)

def list_rendered_images_and_csv(ProjectDir, QuPathApp):
    # CSV Datei anzeigen
    csv_dir = os.path.join(ProjectDir, 'OPSCCnet')
    today_str = datetime.date.today().strftime('%Y%m%d')
    csv_files = [f for f in os.listdir(csv_dir) if f.startswith(today_str) and f.endswith('.csv')]
    if csv_files:
        csv_path = os.path.join(csv_dir, csv_files[0])
        df = pd.read_csv(csv_path, sep=";")
        st.write(df)

    # Bilder anzeigen
    rendered_dir = os.path.join(ProjectDir, 'rendered')
    images = [f for f in os.listdir(rendered_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    for image in images:
        display_name = image.replace('.png', '')
        st.write(display_name)  # Angepasster Name des Bildes
        image_path = os.path.join(rendered_dir, image)
        st.image(image_path)
        # -- funktioniert nicht
        #button_key = f"open_{display_name}" 
        #if button_key not in st.session_state:
        #    st.session_state[button_key] = False

        #if st.button(f"Open {display_name} in QuPath"):
        #    st.session_state[button_key] = True

        #if st.session_state[button_key]:
        #    open_image_in_qupath(QuPathApp, ProjectDir, display_name)
        #    st.stop()

 
            

st.title('OPSCCnet')
QuPathApp = st.text_input('QuPath APP directory:', 'MacOS: /Applications/QuPath.app/Contents/MacOS/QuPath   Linux: /somewhere/QuPath043/QuPath-0.4.3-Linux/QuPath/bin/QuPath')
WSIdir = st.text_input('Directory for virtual whole slide images:', '')
OPSCCdir = st.text_input('OPSCCnet directory:', '')
ProjectDir = st.text_input('QuPath project directory:', '')

if st.button('Run OPSCCnet'):
    run_script(QuPathApp, WSIdir, OPSCCdir, ProjectDir)
    list_rendered_images_and_csv(ProjectDir, QuPathApp)