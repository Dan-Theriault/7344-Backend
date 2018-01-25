# AUTHOR: Daniel Theriault
# DATE: 2018-01-16
# REV: 1

# This is a NixOps configuration file.
# It specifies a server configuration, which NixOps can then deploy to arbitrary backends (physical hosts, VMs, AWS instances, etc.)

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

  projectBackend = stdenv.mkDerivation rec {
    name = "JD-backend-1.0";

    src = pkgs.fetchgitLocal {
      owner = "";
      repo = "";
      rev = "";
      sha256 = "";
    };

    buildInputs = [
      myPython
    ];

    installPhase = ''
      python src/init.py
    '';

      # TODO: INIT PostGres
      # - import models
      # - db.create_all() + db.session.commit()

    meta = {
      platforms = stdenv.lib.platforms.linux;
    };
  };
in
{
  network.description = "Backend network for Georgia Tech CS Capstone Project";

  # Securing the database is easier if its not exposed over the network
  # So, until performance requires otherwise, the backend is a single host
  monolith = 
    { config, pkgs, ... }:
    {
      services.postgresql.enable = true;

      environment.systemPackages = [
        myPython
        projectBackend
      ];

     systemd.services.projectBackend = {
        description = "GT Junior Design Project Backend Daemon";

        environment = {
          DATABASE_URL = "postgresql+psycopg2:///design_dev"; 
        };

        serviceConfig = {
          Type = "forking";
          ExecStart = "/usr/bin/env python";# TODO: backend binary path
          Restart = "on-failure";
        };

        wantedBy = [ "multi-user.target" ];
        wants = [ "network-online.target" ];
        after = [ "network-online.target" ];
      };
    };
}
