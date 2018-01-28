with import <nixpkgs> {};

let 
  this = "Design-Backend";
  ESSBackend = pkgs.python3Packages.buildPythonPackage rec {
    pname = "ESSBackend";
    version = "0.1.1";
    name = "${pname}-${version}";
    src = ./.;
    # buildInputs = with python3Packages; [
    #   bcrypt
    #   flask
    #   flask_sqlalchemy
    #   flask_migrate
    #   psycopg2
    # ];
    postFixup = "";
    doCheck = false;
  };
in
stdenv.mkDerivation {
  name = this;
  buildInputs = [
    (python3Full.buildEnv.override rec {
      ignoreCollisions = true;
      extraLibs = with python3Packages; [
        bcrypt
        flask
        flask_sqlalchemy
        flask_migrate
        psycopg2

        # ESSBackend
      ];
    })
    mypy
    fish
  ];

  shellHook = ''
    ${pkgs.fish}/bin/fish 
  '';
  NIX_SHELL = this;
}
