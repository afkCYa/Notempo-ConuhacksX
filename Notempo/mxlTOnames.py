import zipfile
import os
import xml.etree.ElementTree as ET
from music21 import converter, note, chord
import shutil
import tempfile

ACCIDENTAL_SYMBOLS = {
    11: "",  # for natural
    1: "#",
    -1: "b",
}


def accidental_string(count):
    if count is None:
        return ""

    # music21 uses floats (1.0, -1.0, etc.)
    count = int(round(count))

    if 2 >= count > 0:
        return "#" * count
    elif count < 0:
        return "b" * abs(count)
    return ""


def process_file(input_path, output_dir=None):
    """Process a .mxl or .musicxml/.xml file and produce annotated outputs.

    Args:
        input_path: Path to input file (must exist).
        output_dir: Directory where outputs will be saved (defaults to input file dir).

    Returns:
        annotated_musicxml_path (str): Path to the created annotated MusicXML file.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(input_path)) or os.getcwd()

    basename = os.path.basename(input_path)
    sheetname = basename.split(".")[0]

    # Use a temp dir for safe extraction when needed
    temp_dir = None

    try:
        if input_path.lower().endswith('.mxl'):
            temp_dir = tempfile.mkdtemp(prefix=f"mxl_extract_{sheetname}_")

            with zipfile.ZipFile(input_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            container_path = os.path.join(temp_dir, "META-INF", "container.xml")
            if not os.path.exists(container_path):
                raise FileNotFoundError("container.xml not found in MXL archive.")

            tree = ET.parse(container_path)
            root = tree.getroot()

            rootfile_elem = None
            for elem in root.iter():
                if elem.tag.endswith("rootfile"):
                    rootfile_elem = elem
                    break

            if rootfile_elem is None:
                raise ValueError("No rootfile entry found in container.xml")

            musicxml_rel_path = rootfile_elem.attrib.get("full-path")
            if not musicxml_rel_path:
                raise ValueError("rootfile found, but no full-path attribute")

            musicxml_path = os.path.join(temp_dir, musicxml_rel_path)
            if not os.path.exists(musicxml_path):
                raise FileNotFoundError(f"MusicXML score not found: {musicxml_path}")

        elif input_path.lower().endswith('.musicxml') or input_path.lower().endswith('.xml'):
            musicxml_path = input_path

        else:
            raise ValueError("Unsupported file type. Use .mxl or .musicxml/.xml")

        # Parse
        score = converter.parse(musicxml_path)

        # Key analysis
        key = score.analyze("key")
        key_sig_alter = {p.step: p.alter for p in key.pitches}

        letter_output = []
        solfege_output = []

        solfege_map = {
            "C": "Do",
            "D": "Re",
            "E": "Mi",
            "F": "Fa",
            "G": "Sol",
            "A": "La",
            "B": "Ti",
        }

        # Iterate each part and measure so we can track accidentals that last for the
        # remainder of the measure (i.e., explicit naturals should affect later notes in
        # the same measure).
        for part in score.parts:
            for measure in part.getElementsByClass('Measure'):
                # Start each measure with the key signature alters
                current_alter = dict(key_sig_alter)

                for n in measure.notesAndRests:
                    # Single note
                    if isinstance(n, note.Note):
                        step = n.pitch.step

                        # If this note shows an explicit accidental (displayed), it updates
                        # the current alter for the rest of the measure for that step.
                        acc = getattr(n.pitch, 'accidental', None)
                        if acc is not None and getattr(acc, 'alter', None) is not None and getattr(acc, 'displayStatus', False) is True:
                            # Use actual accidental alter (0 == natural, 1 == sharp, -1 == flat, ...)
                            current_alter[step] = int(round(acc.alter))

                        total_alter = current_alter.get(step, 0)

                        annotated = step + accidental_string(total_alter)
                        letter_output.append(annotated)
                        solfege_output.append(solfege_map[step])

                        n.addLyric(annotated)
                        n.addLyric(solfege_map[step])

                    # Chords
                    elif isinstance(n, chord.Chord):
                        annotated_steps = []
                        base_steps = []

                        for p in n.pitches:
                            step = p.step
                            base_steps.append(step)

                            # If the pitch in the chord has an explicit accidental, update state
                            acc = getattr(p, 'accidental', None)
                            if acc is not None and getattr(acc, 'alter', None) is not None and getattr(acc, 'displayStatus', False) is True:
                                current_alter[step] = int(round(acc.alter))

                            total_alter = current_alter.get(step, 0)
                            annotated_steps.append(step + accidental_string(total_alter))

                        letter_output.append("[" + "|".join(annotated_steps) + "]")
                        solfege_output.append("[" + "|".join(solfege_map[s] for s in base_steps) + "]")

                        n.addLyric("|".join(annotated_steps))
                        n.addLyric("|".join(solfege_map[s] for s in base_steps))

        # Write outputs
        letterfile = os.path.join(output_dir, sheetname + "_letters.txt")
        with open(letterfile, "w", encoding="utf-8") as f:
            f.write(" ".join(letter_output))

        solfegefile = os.path.join(output_dir, sheetname + "_solfege.txt")
        with open(solfegefile, "w", encoding="utf-8") as f:
            f.write(" ".join(solfege_output))

        annotated_path = os.path.join(output_dir, sheetname + "_annotated.musicxml")
        score.write("musicxml", annotated_path)

        return annotated_path

    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process MXL/MusicXML and add annotations.")
    parser.add_argument("input", help="Input .mxl or .musicxml file")
    parser.add_argument("--out", help="Output directory (optional)", default=None)
    args = parser.parse_args()

    out = process_file(args.input, output_dir=args.out)
    print("Created:", out)
