"""
harmony_analyzer/analyze.py
Analizador armónico local usando music21.
Uso: python analyze.py "Am7 | D7 | Gmaj7 | Cmaj7"
     python analyze.py --file progresiones.txt
"""

import sys
import json
import argparse
import re
from typing import Optional

try:
    from music21 import chord, key, roman, pitch, harmony, stream, note
except ImportError:
    print("ERROR: music21 no está instalado. Ejecutá: pip install music21")
    sys.exit(1)


# ── NORMALIZACIÓN DE ACORDES ──────────────────────────────────────────────────

CHORD_ALIASES = {
    # Mayores
    "maj7": "M7", "maj9": "M9", "maj6": "M6",
    "^7": "M7", "^9": "M9",
    # Menores
    "m7b5": "ø7", "m7b5": "ø7", "min7": "m7", "min": "m",
    # Dominantes
    "dom7": "7", "dom": "7",
    # Disminuidos
    "dim7": "o7", "dim": "o",
    # Aumentados
    "aug": "+",
    # Notación de sostenido/bemol
    "#": "#", "b": "-",
}

NOTE_MAP = {
    "Db": "C#", "Eb": "D#", "Fb": "E", "Gb": "F#",
    "Ab": "G#", "Bb": "A#", "Cb": "B",
    "C#": "C#", "D#": "D#", "F#": "F#", "G#": "G#", "A#": "A#",
}


def normalize_chord_name(name: str) -> str:
    """Normaliza nombre de acorde para music21."""
    name = name.strip()
    # Extraer raíz
    match = re.match(r'^([A-G][b#]?)(.*)', name)
    if not match:
        return name
    root, quality = match.group(1), match.group(2)
    # Normalizar bemoles en la raíz
    if root in NOTE_MAP:
        root = NOTE_MAP[root]
    # Normalizar calidad
    quality = quality.replace("maj7", "M7").replace("maj9", "M9").replace("maj", "")
    quality = quality.replace("m7b5", "ø7").replace("ø", "ø7") if "ø7" not in quality else quality
    quality = quality.replace("dim7", "o7").replace("dim", "o")
    quality = quality.replace("min", "m").replace("M ", "")
    quality = quality.replace("sus4", "sus4").replace("sus2", "sus2")
    quality = quality.replace("aug", "+")
    return root + quality


def parse_progression(text: str) -> list[str]:
    """Parsea una progresión en texto a lista de acordes."""
    # Separar por | o coma o salto de línea
    chords_raw = re.split(r'[|,\n]+', text)
    result = []
    for token in chords_raw:
        # Cada token puede tener múltiples acordes separados por espacio
        parts = token.strip().split()
        for part in parts:
            part = part.strip()
            if part and re.match(r'^[A-G]', part):
                result.append(part)
    return result


# ── ANÁLISIS ARMÓNICO ─────────────────────────────────────────────────────────

def chord_to_music21(chord_name: str) -> Optional[harmony.ChordSymbol]:
    """Convierte nombre de acorde a objeto music21."""
    try:
        normalized = normalize_chord_name(chord_name)
        cs = harmony.ChordSymbol(normalized)
        return cs
    except Exception:
        try:
            # Fallback: intentar con el nombre original
            cs = harmony.ChordSymbol(chord_name)
            return cs
        except Exception:
            return None


def detect_key(chord_names: list[str]) -> Optional[key.Key]:
    """Detecta tonalidad usando music21 KeyAnalyzer."""
    try:
        s = stream.Score()
        p = stream.Part()
        for name in chord_names:
            cs = chord_to_music21(name)
            if cs:
                p.append(cs)
        s.append(p)
        detected = s.analyze('key')
        return detected
    except Exception as e:
        return None


def get_roman_numeral(chord_name: str, detected_key: key.Key) -> dict:
    """Obtiene el grado romano y función armónica de un acorde."""
    try:
        cs = chord_to_music21(chord_name)
        if not cs:
            return {"roman": "?", "function": "unknown", "degree": None}

        rn = roman.romanNumeralFromChord(cs, detected_key)
        roman_str = rn.figure

        # Clasificar función armónica
        degree = rn.scaleDegree
        mode = detected_key.mode

        if degree == 1:
            function = "tonic"
        elif degree == 2:
            function = "supertonic"
        elif degree == 3:
            function = "mediant"
        elif degree == 4:
            function = "subdominant"
        elif degree == 5:
            function = "dominant"
        elif degree == 6:
            function = "submediant"
        elif degree == 7:
            function = "leading_tone"
        else:
            function = "chromatic"

        # Detectar tonicizaciones comunes
        if cs.chordKind in ['dominant-seventh', 'dominant'] and degree != 5:
            function = f"V7/{roman_str[roman_str.find('/')+1:] if '/' in roman_str else '?'}"

        return {
            "roman": roman_str,
            "function": function,
            "degree": degree,
        }
    except Exception as e:
        return {"roman": "?", "function": "unknown", "degree": None}


def analyze(progression_text: str) -> dict:
    """
    Analiza una progresión de acordes.
    Input:  "Am7 | D7 | Gmaj7 | Cmaj7"
    Output: dict con key, chords, roman numerals, functions
    """
    chord_names = parse_progression(progression_text)
    if not chord_names:
        return {"error": "No se encontraron acordes válidos", "input": progression_text}

    # Detectar tonalidad
    detected_key = detect_key(chord_names)
    key_str = str(detected_key) if detected_key else "unknown"

    # Analizar cada acorde
    chords_analysis = []
    for name in chord_names:
        entry = {"chord": name, "normalized": normalize_chord_name(name)}
        if detected_key:
            rn_data = get_roman_numeral(name, detected_key)
            entry.update(rn_data)
        else:
            entry.update({"roman": "?", "function": "unknown", "degree": None})
        chords_analysis.append(entry)

    return {
        "input": progression_text,
        "chord_count": len(chord_names),
        "key": key_str,
        "key_tonic": detected_key.tonic.name if detected_key else None,
        "key_mode": detected_key.mode if detected_key else None,
        "confidence": round(detected_key.correlationCoefficient, 3) if detected_key else None,
        "chords": chords_analysis,
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Analizador armónico usando music21",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python analyze.py "Am7 | D7 | Gmaj7 | Cmaj7"
  python analyze.py "Dm7b5 | G7 | Cm7 | Cm7"
  python analyze.py --file progresiones.txt
  python analyze.py "Am7 | D7 | Gmaj7" --output resultado.json
        """
    )
    parser.add_argument("progression", nargs="?", help="Progresión de acordes en texto")
    parser.add_argument("--file", "-f", help="Archivo de texto con progresiones (una por línea)")
    parser.add_argument("--output", "-o", help="Guardar resultado en archivo JSON")
    parser.add_argument("--pretty", "-p", action="store_true", default=True,
                        help="Salida JSON formateada (default: True)")

    args = parser.parse_args()

    results = []

    if args.file:
        try:
            with open(args.file, 'r') as f:
                lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
            for line in lines:
                print(f"Analizando: {line[:60]}...", file=sys.stderr)
                results.append(analyze(line))
        except FileNotFoundError:
            print(f"ERROR: No se encontró el archivo {args.file}", file=sys.stderr)
            sys.exit(1)
    elif args.progression:
        results.append(analyze(args.progression))
    else:
        # Modo interactivo
        print("Ingresá una progresión (o 'salir' para terminar):", file=sys.stderr)
        while True:
            try:
                line = input("> ").strip()
                if line.lower() in ('salir', 'exit', 'quit'):
                    break
                if line:
                    result = analyze(line)
                    print(json.dumps(result, indent=2, ensure_ascii=False))
            except (EOFError, KeyboardInterrupt):
                break
        return

    output = results[0] if len(results) == 1 else results
    json_str = json.dumps(output, indent=2 if args.pretty else None, ensure_ascii=False)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(json_str)
        print(f"Resultado guardado en {args.output}", file=sys.stderr)
    else:
        print(json_str)


if __name__ == "__main__":
    main()
