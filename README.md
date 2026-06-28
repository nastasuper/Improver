# Harmony Analyzer

Analizador armónico local usando music21.  
Detecta tonalidad y genera Roman numerals (estilo Berklee) para progresiones de acordes de jazz.

---

## Instalación

```bash
pip install music21
```

---

## Uso

### Progresión directa
```bash
python analyze.py "Am7 | D7 | Gmaj7 | Cmaj7"
```

### Desde archivo
```bash
python analyze.py --file progresiones_ejemplo.txt
```

### Guardar resultado en JSON
```bash
python analyze.py "Dm7 | G7 | Cmaj7" --output resultado.json
```

### Modo interactivo
```bash
python analyze.py
> Am7 | D7 | Gmaj7 | Cmaj7
> salir
```

---

## Ejemplo de output

Input: `"Am7 | D7 | Gmaj7 | Cmaj7"`

```json
{
  "input": "Am7 | D7 | Gmaj7 | Cmaj7",
  "chord_count": 4,
  "key": "G major",
  "key_tonic": "G",
  "key_mode": "major",
  "confidence": 0.847,
  "chords": [
    { "chord": "Am7",   "normalized": "Am7",   "roman": "ii7",   "function": "supertonic", "degree": 2 },
    { "chord": "D7",    "normalized": "D7",    "roman": "V7",    "function": "dominant",   "degree": 5 },
    { "chord": "Gmaj7", "normalized": "GM7",   "roman": "IM7",   "function": "tonic",      "degree": 1 },
    { "chord": "Cmaj7", "normalized": "CM7",   "roman": "IVM7",  "function": "subdominant","degree": 4 }
  ]
}
```

---

## Separadores aceptados

Los acordes se pueden separar con `|`, `,`, espacios o saltos de línea:

```
Am7 | D7 | Gmaj7 | Cmaj7
Am7, D7, Gmaj7, Cmaj7
Am7 D7 Gmaj7 Cmaj7
```

---

## Notación soportada

| Tipo | Ejemplos |
|------|---------|
| Mayor | `Cmaj7`, `Fmaj9`, `Bb6` |
| Menor | `Am7`, `Dm9`, `Gm6` |
| Dominante | `G7`, `C7`, `F#7` |
| Semidisminuido | `Bm7b5`, `F#ø7` |
| Disminuido | `Bdim7`, `Bo7` |
| Sus | `Csus4`, `Gsus2` |

---

## Notas

- La detección de tonalidad usa el algoritmo de Krumhansl-Schmuckler de music21.
- El `confidence` indica qué tan fuerte es la correlación con la tonalidad detectada (0–1).
- Para progresiones ambiguas (blues, modal, Giant Steps) el confidence suele ser bajo (<0.6).
