{pkgs ? import <nixpkgs> {}}: let
  libs = with pkgs; [
    stdenv.cc.cc.lib
    zlib
    libGL
    glib.out
    libx11
  ];
in
  pkgs.mkShell
  {
    packages =
      libs
      ++ (with pkgs; [
        (python313 .withPackages (p:
          with p; [
            # let venv handle this
            # matplotlib
            # scipy
            pyqt6
          ]))
        (python313Packages.matplotlib.override {
          enableQt = true;
        })
      ]);

    LD_LIBRARY_PATH = "${pkgs.lib.makeLibraryPath libs}:$LD_LIBRARY_PATH";

    shellHook = ''
      source venv/bin/activate
    '';
  }
