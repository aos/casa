{
  description = "casa";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        poetry-env = pkgs.poetry2nix.mkPoetryEnv {
          projectDir = ./.;
          editablePackageSources.casa = ./casa;
          preferWheels = true;
        };
      in
      {
        packages = {
          default = pkgs.poetry2nix.mkPoetryApplication {
            projectDir = ./.;
            preferWheels = true;
          };
        };

        devShell = poetry-env.env.overrideAttrs (old: {
          nativeBuildInputs = with pkgs; old.nativeBuildInputs ++ [
            pkgs.ansible
            pkgs.python3Packages.poetry
            pkgs.python3Packages.flake8
          ];
        });
      });
}
