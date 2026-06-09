{pkgs ? import <nixpkgs> {}}: let
  libs = with pkgs; [
    stdenv.cc.cc.lib
    zlib
    libGL
    glib.out
    libx11
    freeglut
    libGLU
    libxcursor
  ];
in
  pkgs.mkShell
  {
    packages =
      libs
      ++ [
        pkgs.conda

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
            ipython

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
        export MKL_NUM_THREADS=$(nproc)
        export OMP_NUM_THREADS=$(nproc)
        if [ ! -d venv ]; then
          python -m venv venv
          source venv/bin/activate
          pip install -r requirements.txt
        else
          source venv/bin/activate
        fi
      '';
  }
