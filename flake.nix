{
  description = "casa";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
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
          docker = let
            app = self.packages.${system}.default;
          in pkgs.dockerTools.buildLayeredImage {
            name = "aos/${app.pname}";
            tag = "latest";
            contents = [ app ];

            config = {
              Cmd = [ "${app}/bin/casa" ];
            };
          };
          provision = pkgs.writeShellScriptBin "provision-plug" ''
            "${pkgs.ansible}/bin/ansible-playbook" --ask-vault-pass ./provision.yml
          '';
        };

        devShell = poetry-env.env.overrideAttrs (old: {
          nativeBuildInputs = with pkgs; old.nativeBuildInputs ++ [
            pkgs.python3Packages.poetry
            pkgs.python3Packages.flake8
          ];
        });
      });
}
