#!/usr/bin/env python3
import qrcode
import argparse
import os
import subprocess

def generate_qr_code(text):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=0,
    )
    qr.add_data(text)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    qr_list = [[int(bit) for bit in row] for row in matrix]
    return qr_list

def generate_wifi_string(ssid, password, encryption='WPA', hidden=False):
    """Generate WiFi QR code string in ZXing format."""
    hidden_flag = 'true' if hidden else 'false'
    return f"WIFI:T:{encryption};S:{ssid};P:{password};H:{hidden_flag};;"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate a WiFi QR-code card for 3D printing.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate WiFi card for a network
  %(prog)s --ssid "MyNetwork" --password "MyPassword123"

  # Generate WiFi card with WEP encryption
  %(prog)s --ssid "MyNetwork" --password "MyPassword123" --encryption WEP

  # Generate card with custom text
  %(prog)s --raw "WIFI:S:MyNet;T:WPA;P:secret;;"
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--ssid', '-s', help='WiFi network SSID')
    group.add_argument('--raw', '-r', help='Raw string to encode (for custom QR codes)')

    parser.add_argument('--password', '-p', help='WiFi network password (required with --ssid)')
    parser.add_argument('--encryption', '-e',
                        choices=['WPA', 'WEP', 'nopass'],
                        default='WPA',
                        help='WiFi encryption type (default: WPA)')
    parser.add_argument('--hidden', action='store_true',
                        help='Set if the network is hidden')
    parser.add_argument('--layer-height', '-l',
                        type=float,
                        default=0.2,
                        help='Print layer height in mm (default: 0.2)')
    parser.add_argument('--magnet-diameter',
                        type=float,
                        help='Diameter of magnet holes in mm (requires --magnet-depth)')
    parser.add_argument('--magnet-depth',
                        type=float,
                        help='Depth of magnet holes in mm (requires --magnet-diameter)')

    args = parser.parse_args()

    # Validate that password is provided when using --ssid
    if args.ssid and not args.password:
        parser.error("--password is required when using --ssid")

    # Validate that both magnet parameters are provided together
    if (args.magnet_diameter is not None) != (args.magnet_depth is not None):
        parser.error("--magnet-diameter and --magnet-depth must be used together")

    # Generate the text to encode
    if args.raw:
        text = args.raw
    else:
        text = generate_wifi_string(args.ssid, args.password, args.encryption, args.hidden)

    print(f"Encoding: {text}")

    # Create output directory if it doesn't exist
    if not os.path.exists("./output"):
        os.makedirs("./output")

    # Generate QR code and write to file
    qr_list = generate_qr_code(text)
    with open("./qrcode-matrix.scad", 'w') as f:
        f.write('qrData = ')
        f.write(str(qr_list) + ';')

    # Generate STL files using OpenSCAD
    # Provide a path to openscad executable. Leave unchanged if openscad can be found in PATH variable (openscad can be run as a command from shell).
    openscad_path = 'openscad'

    # Build OpenSCAD parameter list
    openscad_params = [
        '-D', f'layerHeight={args.layer_height}'
    ]

    # Add SSID and password if using --ssid mode
    if args.ssid:
        openscad_params.extend([
            '-D', f'wifiSSID="{args.ssid}"',
            '-D', f'wifiPassword="{args.password}"'
        ])

    # Add magnet hole parameters if provided
    if args.magnet_diameter is not None and args.magnet_depth is not None:
        openscad_params.extend([
            '-D', f'magnetDiameter={args.magnet_diameter}',
            '-D', f'magnetDepth={args.magnet_depth}'
        ])

    print("Generating qrcode.stl...")
    subprocess.run([
        openscad_path, './wifi-card.scad',
        '-D', 'qrCodeOnly=true',
        *openscad_params,
        '-o', './output/qrcode.stl'
    ], check=True)

    print("Generating main_body.stl...")
    subprocess.run([
        openscad_path, './wifi-card.scad',
        '-D', 'qrCodeOnly=false',
        '-D', 'nfcTag=true',
        *openscad_params,
        '-o', './output/main_body.stl'
    ], check=True)

    print("Done! STL files saved in ./output/")

