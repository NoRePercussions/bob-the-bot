{
  description = "Bob the discord bot, revived";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    flake-utils.url = "github:numtide/flake-utils";

    poetry2nix.url = "github:nix-community/poetry2nix";
    poetry2nix.inputs.nixpkgs.follows = "nixpkgs";
  };
  outputs = {
    self,
    nixpkgs,
    flake-utils,
    poetry2nix,
  } @ inputs:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
        poetry2nix = inputs.poetry2nix.lib.mkPoetry2Nix {inherit pkgs;};

        overrides = poetry2nix.overrides.withDefaults (self: super: {
          profanity = super.itsdangerous.overridePythonAttrs (
            old: {
              buildInputs = (old.buildInputs or []) ++ [self.setuptools];
            }
          );
        });

        app = poetry2nix.mkPoetryApplication {
          projectDir = ./.;
          inherit overrides;
        };

        mkScriptApp = program: {
          type = "app";
          inherit program;
        };
      in rec {
        apps = rec {
          default = bot;
          bot = mkScriptApp "${app}/bin/bot";
          scrape = mkScriptApp "${app}/bin/scrape";
          process = mkScriptApp "${app}/bin/process";

          lint = {
            type = "app";
            program = "${packages.bob-lint}/bin/bob-lint";
          };
        };

        packages = {
          bob-lint = pkgs.writeShellApplication {
            name = "bob-lint";

            runtimeInputs = with pkgs; [
              alejandra
              black
            ];

            text = with pkgs; ''
              echo "Formatting with Alejandra..."
              alejandra .
              echo "Formatting with Black..."
              black ./**/*.py
            '';
          };
        };
      }
    );
}
