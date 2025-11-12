{pkgs}:
pkgs.python313Packages.buildPythonPackage rec {
  pname = "stadcal";
  version = "0.0.1";
        format = "pyproject";
  src = ./src;
  propagatedBuildInputs = [
    pkgs.python3Packages.apscheduler
    pkgs.python3Packages.flask
    pkgs.python3Packages.gunicorn
    pkgs.python3Packages.icalendar
    pkgs.python3Packages.selenium
    pkgs.firefox
  ];
  build-system = [
    pkgs.python3Packages.setuptools
  ];
  buildInputs = [
    pkgs.firefox
  ];
}
