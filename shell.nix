{pkgs ? import <nixpkgs> {}}: let
  libs = with pkgs; [
    stdenv.cc.cc.lib
    zlib
    libGL
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

        (pkgs.python313.withPackages (p:
          with p; [
            napari
            requests

            pyqt6
            pyqt5

            debugpy
            ipython
            (matplotlib.override {
              enableQt = true;
            })
          ]))
      ];

    shellHook = let
      q5 = with pkgs.qt5; "${qtbase}/${qtbase.qtPluginPrefix}:";
      q6 = with pkgs.qt6; "${qtbase}/${qtbase.qtPluginPrefix}";
      q = q5 + q6;
      l = pkgs.lib.makeLibraryPath libs;
    in
      /*
      bash
      */
      ''
        # export MKL_NUM_THREADS=$(nproc)
        # export OMP_NUM_THREADS=$(nproc)
        export PYTHONPATH="$(pwd):$PYTHONPATH"

        export LD_LIBRARY_PATH="${l}:$LD_LIBRARY_PATH";
        export QT_PLUGIN_PATH="${q}:$QT_PLUGIN_PATH";

        if [ ! -d venv ]; then
          python -m venv venv
          source venv/bin/activate
          pip install -r requirements.txt
          pip install --no-index --find-links wheels --no-deps fmm3dpy --force-reinstall
        else
          source venv/bin/activate
        fi
      '';
  }
