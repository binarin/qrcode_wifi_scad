# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python + OpenSCAD project that generates 3D-printable WiFi QR-code cards. The workflow involves:
1. Python script generates QR code data and writes it to `qrcode-matrix.scad`
2. OpenSCAD renders two STL files: the QR code layer and the main card body
3. Both STLs are printed separately using Z-hop technique for two-color first layer

## Development Environment

Use Nix flake for development:
```bash
nix develop
# Or with direnv (already configured)
direnv allow
```

This provides:
- `openscad-unstable` - OpenSCAD for 3D model generation
- `python3` with `qrcode` package

## Common Commands

### Generate STL Files

With WiFi credentials:
```bash
python generate.py --ssid "NetworkName" --password "password123"
```

With raw QR code data:
```bash
python generate.py --raw "WIFI:S:MyNetwork;T:WPA;P:secret;;"
```

Additional options:
- `--encryption {WPA,WEP,nopass}` - Set encryption type (default: WPA)
- `--hidden` - Mark network as hidden

Output files are saved to `./output/qrcode.stl` and `./output/main_body.stl`.

### Manual OpenSCAD Rendering

Generate QR code layer only:
```bash
openscad wifi-card.scad -D qrCodeOnly=true -o output/qrcode.stl
```

Generate main body with NFC tag void:
```bash
openscad wifi-card.scad -D qrCodeOnly=false -D nfcTag=true -o output/main_body.stl
```

## Architecture

### Data Flow

1. **generate.py** - Python script that:
   - Takes WiFi credentials or raw text input
   - Generates QR code using `qrcode` library
   - Writes QR matrix as Python list to `qrcode-matrix.scad`
   - Invokes OpenSCAD to generate both STL files

2. **qrcode-matrix.scad** - Auto-generated file containing:
   - `qrData` variable: 2D array representing QR code matrix (1=black, 0=white)
   - This file is regenerated on each `generate.py` run

3. **wifi-card.scad** - Main OpenSCAD model:
   - Includes `qrcode-matrix.scad` for QR data
   - Includes `wifi-logo/logo.scad` for WiFi logo
   - Renders either QR code layer or main card body based on `qrCodeOnly` parameter
   - Customizable parameters via OpenSCAD Customizer (Window → Customizer)

4. **wifi-logo/logo.scad** - WiFi logo composition:
   - Imports multiple SVG files (w.svg, i.svg, f.svg, i_2.svg, outline.svg, cut.svg)
   - Uses relative paths for SVG files
   - Combines SVGs using CSG operations (union/difference)

### Key OpenSCAD Parameters

Edit in `wifi-card.scad` or use OpenSCAD Customizer:

- `layerHeight` (default: 0.2) - Print layer height; determines indent depth
- `cardSize` (default: [70, 120, 4]) - Card dimensions [width, length, height]
- `margin` (default: 6) - Distance from card edge to QR code
- `nfcTag` (default: false) - Whether to include NFC tag void
- `nfcTagSize` (default: [0.4, 13]) - NFC tag [height, radius]
- `qrOffsetVertical`/`qrOffsetHorizontal` - Clearances for QR code indent

### Z-Hop Printing Workflow

The model is designed for two-color first layer printing:
1. Print `qrcode.stl` in first color (don't remove from bed)
2. Change filament to second color
3. Configure Z-hop height slightly higher than layer height (~0.4mm for 0.2mm layers)
4. Print `main_body.stl` - nozzle will hop over first layer to avoid collision

## Important Implementation Details

### QR Code Generation Module (wifi-card.scad:36-63)

The `qrCode()` module:
- Takes 2D array from `qrData` and converts to 3D geometry
- Uses `offset()` to add clearance around QR pixels
- Calculates cell size based on card dimensions and QR matrix size
- There's an experimental `gap` parameter (currently 0) for pixel separation

### File Path Handling

SVG imports in `wifi-logo/logo.scad` use relative paths. If moving files, ensure paths remain relative to the logo.scad file location.

### OpenSCAD Path Configuration

The `openscad_path` variable in generate.py:79 can be customized if `openscad` is not in PATH.
