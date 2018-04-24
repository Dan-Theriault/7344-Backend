# AUTHOR: Daniel Theriault
# This is a NixOps configuration file.
# Specifies a server configuration, which NixOps can then deploy to arbitrary backends (physical hosts, VMs, AWS instances, etc.)

{
  network.description = "Backend network for Georgia Tech CS Capstone Project";

  # This configuration deploys our backend and all services on a single host.
  # This configuration will not scale infinitely; it is primarily intended for testing purposes.
  # I did make every effort to deliver good performance; on a sufficiently powerful server, this configuration should server well.
  monolith = 
    { config, pkgs, ... }:
    let
      # This is the actual backend package
      ESSBackend = pkgs.python3Packages.buildPythonPackage rec {
        pname = "ESSBackend";
        version = "2.0beta";
        name = "${pname}-${version}";
        src = ./.;
        doCheck = false;
        # postFixup = "";
      };
      myPython = pkgs.python3.buildEnv.override rec {
        extraLibs = [ pkgs.uwsgi ];
      };

      # define some variables
      database_name = "ess_prod";
      database_user = "uwsgi";
      secret = builtins.readFile ./secrets/ess.txt; #TODO: create this file. 256-char random str.

      envvars = { 
        DATABASE_URI = "postgresql+psycopg2:///${database_name}"; 
        ESS_SECRET = "'${secret}'";
      };
    in
    {
      # We chose to use postgres for this backend because it is free, feature-complete, and really fast.
      # However, we used an ORM, meaning it's possible to change to another SQL database if you prefer.
      services.postgresql = {
        enable = true;
        # This creates our database, and authorizes the backend-running user to access it
        # Providing our backend-running user with the minimum permissions required is good security practice.
        initialScript = builtins.toFile "psql-init.sh" ''
          CREATE ROLE ${database_user} WITH LOGIN;
          CREATE DATABASE ${database_name};
          ALTER DATABASE ${database_name} OWNER TO ${database_user};
          \connect ${database_name};
          ALTER DEFAULT PRIVILEGES GRANT ALL ON TABLES TO ${database_user};
        '';
      };

      # ddclient dynamically informs your domain registrar of this server's IP address.
      # This means you can make this server accessible at a domain name without any manual intervention.
      # However, you do need to manual change this section from the test domain over to a production domain.
      # I use namecheap for my personal and test domains;
      # they're a solid provider, and have good instructions available for dynamic dns.
      services.ddclient = {
        enable = true;
        # TODO: change to production domain. 
        domain = "ess.dtheriault.com";         
        server = "dynamicdns.park-your-domain.com";
        protocol = "namecheap";
        use = "web, web=dynamicdns.park-your-domain.com/getip";
        username = "dtheriault.com"; # TODO: your username is your registered domain
        # TODO: put your dyndns password (from your registrar) in this file
        password = builtins.readFile ./secrets/dyndns.txt; 
      };

      # Port 80 is for http and port 443 is for https
      networking.firewall.allowedTCPPorts = [ 80 443 ];

      # nginx is a http server/proxy.
      # It handles connections from client devices much more robustly than a bare flask application.
      # This instance has also been configured to automatically setup SSL,
      # which encrypts all traffic between this server and client devices.
      # This is required to provide good security to our users.
      services.nginx = {
        enable = true;
        recommendedTlsSettings = true;
        recommendedOptimisation = true;
        recommendedGzipSettings = true;
        recommendedProxySettings = true;
        virtualHosts."ess.dtheriault.com" = { # TODO: Change this to the production domain name
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

      # Runs the backend application in uwsgi.
      # uwsgi makes it easier to interface with nginx,
      # and makes our application much faster by managing multi-processing.
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
              pythonPackages = self: [
                self.bcrypt
                self.flask
                self.flask_migrate
                self.flask_sqlalchemy
                self.psycopg2
                self.sqlalchemy
                ESSBackend
              ];
              chdir = "${ESSBackend}/lib/python3.6/site-packages/ESSBackend/";
              wsgi-file = "app.py";
              callable = "app";
              # module = "ESSBackend.wsgi";
              socket = "/run/uwsgi/ESSBackend.sock";
              chmod-socket = "666";
              env = [ "ESS_SECRET=${secret}" ];
            };
          };
        };
      };

      environment = {
        systemPackages = [ 
          ( myPython.withPackages ( ps: [
            ps.bcrypt
            ps.flask
            ps.flask_migrate
            ps.flask_sqlalchemy
            ps.psycopg2
            ps.sqlalchemy
            ESSBackend
          ] ) )
        ];
        variables = envvars; 
      };

      systemd.globalEnvironment = envvars;

      # This service executes once, at server startup, to set up the database tables required for our application.
      systemd.services.ESSBackendInit = {
        serviceConfig = {
          Type = "oneshot";
          ExecStart = "/run/current-system/sw/bin/python ${ESSBackend}/lib/python3.6/site-packages/ESSBackend/dbinit.py";
          ExecStartPre = "export ESS_SECRET '${secret}'";
          User = "${database_user}";
        };
        description = "Initializes the database tables needed by ESSBackend.";
        environment = envvars;
        before = [ "uwsgi.service" ];
        wantedBy = [ "multi-user.target" ];
        after = [ "postgresql.service" ];
        requires = [ "postgresql.service" ];
      };
    };
}
