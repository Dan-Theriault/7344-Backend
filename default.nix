with import <nixpkgs> {};

let 
  this = "Design-Backend";
in
stdenv.mkDerivation {
  name = this;
  buildInputs = [
    (python2Full.buildEnv.override rec {
      ignoreCollisions = true;
      extraLibs = with python3Packages; [
        bcrypt
        flask
        flask_sqlalchemy
        flask_migrate
        psycopg2
      ];
    })
    mypy
    fish
  ];

  shellHook = ''
    ${pkgs.fish}/bin/fish 
  '';
  DATABASE_URL = "postgresql+psycopg2:///design_dev";
  NIX_SHELL = this;
}
