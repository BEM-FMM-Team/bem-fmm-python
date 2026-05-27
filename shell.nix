{pkgs ? import <nixpkgs> {}}: let
  libs = with pkgs; [
    stdenv.cc.cc.lib
    zlib
    libGL
    glib.out
    libx11
    freeglut
    libGLU
  ];
in
  pkgs.mkShell
  {
    packages =
      libs
      ++ [
        pkgs.ruff
        pkgs.basedpyright
        pkgs.pylint

        pkgs.python313Packages.matplotlib
        (pkgs.python313.withPackages (p:
          with p; [
            # let venv handle this
            # matplotlib
            # scipy
            pyqt6
            debugpy

            # pyglet

            (matplotlib.override {
              enableQt = true;
            })
          ]))
      ];

    LD_LIBRARY_PATH = "${pkgs.lib.makeLibraryPath libs}:$LD_LIBRARY_PATH";

    shellHook =
      /*
      bash
      */
      ''
        export PYTHONPATH="$PYTHONPATH:$PWD"
        if [ ! -d venv ]; then
          python3 -m venv venv
          source venv/bin/activate
          pip install -r requirements.txt
        else
          source venv/bin/activate
        fi
      '';
  }
