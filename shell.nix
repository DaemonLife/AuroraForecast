{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python3
    pkgs.python3Packages.plotext
    pkgs.python3Packages.pandas
    pkgs.python3Packages.requests
  ];
}

