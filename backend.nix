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
      ESSBackend = pkgs.python3Packages.buildPythonApplication rec {
        pname = "ESSBackend";
        version = "0.1.1";
        name = "${pname}-${version}";
        src = pkgs.fetchgitPrivate {
          url="git@github.com:Dan-Theriault/7344-Backend.git"; 
        };
        buildInputs = with pkgs.python3Packages; [
          bcrypt
          flask
          flask_sqlalchemy
          flask_migrate
          psycopg2
        ];
        doCheck = false;
      };
      myPython = pkgs.python3Full.buildEnv.override rec {
        extraLibs = with pkgs.python3Packages; [
          bcrypt
          flask
          flask_migrate
          flask_sqlalchemy
          psycopg2
          sqlalchemy

          ESSBackend
        ] ++ [ pkgs.uwsgi ];
      };
    in
    {
      services.postgresql = {
        enable = true;
        initialScript = builtins.toFile "psql-init.sh" ''
          CREATE USER root WITH SUPERUSER;
          CREATE USER uwsgi WITH SUPERUSER;
          CREATE DATABASE design_dev;
          ALTER DATABASE design_dev OWNER TO uwsgi
        '';
        authentication = ''
          local all all                trust
          host  all all 127.0.0.1/32   trust
          host  all all ::1/128        trust
          host  all all 192.168.1.0/24 trust
        '';
      };

      services.ddclient = {
        enable = true;
        domain = "ess.dtheriault.com";
        server = "dynamicdns.park-your-domain.com";
        protocol = "namecheap";
        use = "web, web=dynamicdns.park-your-domain.com/getip";
        username = "dtheriault.com";
        password = builtins.readFile ./secrets/dyndns;
      };

      networking.firewall.allowedTCPPorts = [ 80 443 ];

      services.nginx = {
        enable = true;
        recommendedTlsSettings = true;
        recommendedOptimisation = true;
        recommendedGzipSettings = true;
        recommendedProxySettings = true;
        virtualHosts."ess.dtheriault.com" = {
          enableACME = true;
          forceSSL = true;
          locations."/" = {
            extraConfig = ''
              include ${pkgs.nginx}/conf/uwsgi_params;
              uwsgi_pass unix:///run/uwsgi/ESSBackend.sock;
            '';
          };
        };
      };

      services.uwsgi = {
        enable = true;
        plugins = [ "python3" ];
        instance = {
          type = "emperor";
          vassals = {
            ESSBackend = {
             # https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html
             # I think this section is literally translated to a wsgi.ini file
              type = "normal";
              pythonPackages = self: with self; [
                bcrypt
                flask
                flask_migrate
                flask_sqlalchemy
                psycopg2
                sqlalchemy
                ESSBackend
              ];
              chdir = "${ESSBackend}/lib/python3.6/site-packages/ESSBackend/";
              wsgi-file = "app.py";
              callable = "app";
              # module = "ESSBackend.wsgi";
              socket = "/run/uwsgi/ESSBackend.sock";
              chmod-socket = "666";
            };
          };
        };
      };

      environment = {
        systemPackages = [ myPython ];
        variables = { DATABASE_URL = "postgresql+psycopg2:///design_dev"; };
      };

      systemd.services.ESSBackendInit = {
        description = "Initializes the database tables needed by ESSBackend.";
        serviceConfig = {
          Type = "oneshot";
          ExecStart = "${myPython}/bin/python ${ESSBackend}/lib/python3.6/site-packages/ESSBackend/init.py";
        };
        before = [ "uwsgi.service" ];
        wantedBy = [ "multi-user.target" ];
        after = [ "postgresql.service" ];
        requires = [ "postgresql.service" ];
      };
    };
}
