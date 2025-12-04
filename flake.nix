{
  description = "WiFi QR-code Card - A script to generate a simple WiFi QR-code card for 3D printing using Python and OpenSCAD";

  inputs = {
    flake-parts.url = "github:hercules-ci/flake-parts";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
  };

  outputs = inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [ "x86_64-linux" ];
      perSystem = { config, self', inputs', pkgs, system, ... }: {
        devShells.default = pkgs.mkShell {
          name = "default-dev-shell";
          meta.description = "Default development shell";
          packages = with pkgs; [
            openscad-unstable
            (python3.withPackages (ps: with ps; [ qrcode ]))
          ];
        };
      };
    };
}
