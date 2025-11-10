{
  description = "Description for the project";

  inputs = {
    flake-parts.url = "github:hercules-ci/flake-parts";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    devshell.url = "github:numtide/devshell";
  };

  outputs =
    inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      imports = [
        inputs.devshell.flakeModule

      ];
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
        "x86_64-darwin"
      ];
      perSystem =
        {
          config,
          self',
          inputs',
          pkgs,
          system,
          ...
        }:
        {
          # Per-system attributes can be defined here. The self' and inputs'
          # module parameters provide easy access to attributes of the same
          # system.

          # Equivalent to  inputs'.nixpkgs.legacyPackages.hello;
          packages.default = pkgs.hello;
          packages.stadcal = let
             stadcal = pkgs.python313Packages.callPackage ./derivation.nix {};
             in  pkgs.python3.withPackages(_: [ stadcal ]);
          nixosModules.stadcal = { config, lib, pkgs, ...}:
            let
              cfg = config.services.stadcal;
            in{
              options.services.stadcal = {
                enable = lib.mkEnableOption "Enable the stadcal http service";
              };
              config = lib.mkIf cfg.enable {
                systemd.services.stadcal = {
                  wantedBy = [ "multi-user.target" ];
                  serviceConfig = {
                    Restart = "on-failure";
                    ExecStart = "${self'.pkgs}/bin/gunicorn stadcal.wsgi:app";
                    DynamicUser = "yes";
                    RuntimeDirectory = "stadcal";
                  };
                };
              };

          };
          devshells.default =
            let
              pwp = pkgs.python313.withPackages (ppkgs: [
                ppkgs.apscheduler
                ppkgs.flask
                ppkgs.gunicorn
                ppkgs.icalendar
                ppkgs.selenium
              ]);
            in
            {
              commands = [
                {
                  help = "start flask local development server";
                  name = "startflask";
                  command = "flask --app ./src/stadcal/wsgi run --host 0.0.0.0 -p 8080 --debug";
                }

              ];
              packages = [
                pwp
                pkgs.firefox
              ];

            };
        };
      flake = {
        # The usual flake attributes can be defined here, including system-
        # agnostic ones like nixosModule and system-enumerating ones, although
        # those are more easily expressed in perSystem.

      };
    };
}
