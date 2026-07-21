{
  description = "bem-fmm-python";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    treefmt-nix.url = "github:numtide/treefmt-nix";
  };

  outputs = {
    self,
    nixpkgs,
    treefmt-nix,
    ...
  }: let
    eachSystem = f:
      nixpkgs.lib.genAttrs nixpkgs.lib.systems.flakeExposed (
        system: f system nixpkgs.legacyPackages.${system}
      );
    treefmtEval = eachSystem (_system: pkgs:
      treefmt-nix.lib.evalModule pkgs (_: {
        projectRootFile = "flake.nix";
        programs.black.enable = true;
      }));
  in {
    formatter = eachSystem (_system: pkgs: treefmtEval.${pkgs.system}.config.build.wrapper);
    checks = eachSystem (_system: pkgs: {
      formatting = treefmtEval.${pkgs.system}.config.build.check self;
    });
    devShells = eachSystem (
      _system: pkgs: {
        default = let
          libs = with pkgs; [
            stdenv.cc.cc.lib
            zlib
            libGL
            libx11
            freeglut
            libGLU
            libxcursor
            libxkbcommon
          ];
        in
          pkgs.mkShell
          {
            packages =
              libs
              ++ (with pkgs; [
                gdb

                ruff
                basedpyright
                black
                pylint

                kdePackages.qttools
              ])
              ++ [
                (pkgs.python313.withPackages (p:
                  with p; [
                    uv
                    pyside6
                    napari
                    scikit-image
                    pooch
                    requests
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
              sh
              */
              ''
                export LD_LIBRARY_PATH="${l}:$LD_LIBRARY_PATH";
                export QT_PLUGIN_PATH="${q}:$QT_PLUGIN_PATH";
                export QT_QPA_PLATFORM=xcb

                source ./dev.sh
              '';
          };
      }
    );
  };
}
