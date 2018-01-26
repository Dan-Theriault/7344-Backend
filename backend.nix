# AUTHOR: Daniel Theriault
# DATE: 2018-01-16
# REV: 1

# This is a NixOps configuration file.
# It specifies a server configuration, which NixOps can then deploy to arbitrary backends (physical hosts, VMs, AWS instances, etc.)


{
  network.description = "Backend network for Georgia Tech CS Capstone Project";

  # Securing the database is easier if its not exposed over the network
  # So, until performance requires otherwise, the backend is a single host
  monolith = 
    { config, pkgs, ... }:
    let
      myPython = pkgs.python3Full.buildEnv.override rec {
        extraLibs = with pkgs.python3Packages; [
          bcrypt
          flask
          flask_migrate
          flask_sqlalchemy
          psycopg2
          sqlalchemy
        ];
      };

      backend = pkgs.stdenv.mkDerivation {
        name = "7144Backend-0.1";

        src = ./src;

        buildInputs = [
          myPython
        ];

        doCheck = false;

        installPhase = ''
          cp -r . $out/
        '';

        meta = {
          platforms = pkgs.stdenv.lib.platforms.linux;
        };
      };
    in
    {
      services.postgresql = {
        enable = true;
        initialScript = builtins.toFile "psql-init.sh" ''
          CREATE DATABASE design_dev;
          CREATE USER root;
          CREATE USER gt7344;
        '';
        authentication = ''
          local all all                trust
          host  all all 127.0.0.1/32   trust
          host  all all ::1/128        trust
          host  all all 192.168.1.0/24 trust
        '';
      };

      environment.systemPackages = [
        myPython
        backend 
      ];

     systemd.services.projectBackend = {
        description = "GT Junior Design Project Backend Daemon";

        environment = {
          DATABASE_URL = "postgresql+psycopg2:///design_dev"; 
        };

        preStart = "python {backend}/init.py";

        serviceConfig = {
          Type = "forking";
          ExecStart = "python {backend}/app.py";
          Restart = "on-failure";
        };

        wantedBy = [ "multi-user.target" ];
      };
    };
}
