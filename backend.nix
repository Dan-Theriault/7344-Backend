# AUTHOR: Daniel Theriault
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

      ESSBackend = pkgs.python3Packages.buildPythonApplication rec {
        pname = "ESSBackend";
        version = "0.1";
        name = "${pname}-${version}";
        src = pkgs.fetchgitPrivate {
          url="git@github.com:Dan-Theriault/7344-Backend.git"; 
        };
        propogatedBuildInputs = myPython;
        preInstallPhase = ''
          cd src
        '';
      };
    in
    {
      services.postgresql = {
        enable = true;
        initialScript = builtins.toFile "psql-init.sh" ''
          CREATE DATABASE design_dev;
          CREATE USER root;
          CREATE USER essb;
        '';
        authentication = ''
          local all all                trust
          host  all all 127.0.0.1/32   trust
          host  all all ::1/128        trust
          host  all all 192.168.1.0/24 trust
        '';
      };

      environment = {
        systemPackages = [
          myPython
          ESSBackend 
        ];
        variables = {
          DATABASE_URL = "postgresql+psycopg2:///design_dev"; 
        };
      };

      systemd.services.ESSBackend = {
        description = "GT Junior Design Project Backend Daemon";

        preStart = "{myPython}/bin/python {backend}/src/init.py";

        serviceConfig = {
          Type = "forking";
          ExecStart = "{myPython}/bin/python {backend}/src/app.py";
          Restart = "on-failure";
        };

        wantedBy = [ "multi-user.target" ];
      };
    };
}
