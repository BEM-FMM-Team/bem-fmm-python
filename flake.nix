{
  description = "bem-fmm-python";

  inputs.nixpkgs.url = "https://channels.nixos.org/nixos-unstable/nixexprs.tar.zst";

  outputs =
    { nixpkgs, ... }:
    let
      inherit (nixpkgs) lib;
      forAll =
        f:
        lib.genAttrs [
          "x86_64-linux"
          "aarch64-linux"
          "x86_64-darwin"
          "aarch64-darwin"
        ] (system: f nixpkgs.legacyPackages.${system});

      # treefmt.toml calls these
      formatters =
        pkgs: with pkgs; [
          treefmt
          black
          isort
          nixfmt
        ];
    in
    {
      # nix fmt, the same as treefmt in the dev shell
      formatter = forAll (
        pkgs:
        pkgs.writeShellApplication {
          name = "treefmt";
          runtimeInputs = formatters pkgs;
          text = ''exec treefmt "$@"'';
        }
      );

      devShells = forAll (
        pkgs:
        let
          # loaded at run time by the PyPI wheels in .venv (numpy, vtk, PySide6),
          # which look for them in the usual system places, not in the nix store
          libs = with pkgs; [
            stdenv.cc.cc.lib
            zstd
            zlib
            libGL
            # the OpenGL driver for amd and intel. The one of the system in
            # /run/opengl-driver is built for the glibc of the system and
            # does not load here once the system is newer than flake.lock
            mesa
            glib
            fontconfig
            freetype
            dbus
            krb5
            libxkbcommon
            wayland
            libx11
            libxext
            libxrender
            libxi
            libxrandr
            libxcursor
            libxfixes
            libsm
            libice
            libxcb
            libxcb-cursor
            libxcb-util
            libxcb-wm
            libxcb-image
            libxcb-keysyms
            libxcb-render-util
          ];
        in
        {
          default = pkgs.mkShell {
            # a plain python, every package comes from pyproject.toml into .venv
            packages =
              with pkgs;
              [
                python314
                uv
                ruff
                basedpyright
              ]
              ++ formatters pkgs
              ++ lib.optionals stdenv.hostPlatform.isLinux [ gdb ];

            shellHook =
              lib.optionalString pkgs.stdenv.hostPlatform.isLinux ''
                # the driver folder of the system comes last, for nvidia
                export LD_LIBRARY_PATH="${lib.makeLibraryPath libs}:/run/opengl-driver/lib''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
                # the 3D view renders through GLX, which Qt only offers on xcb
                export QT_QPA_PLATFORM=xcb
              ''
              + ''
                # PySide6 brings its own Qt, plugins and styles of the desktop Qt
                # (kvantum and the like) make it crash or warn,
                # and nothing from outside may end up in .venv
                unset QT_PLUGIN_PATH QML2_IMPORT_PATH QT_STYLE_OVERRIDE PYTHONPATH
                source ./scripts/dev.sh
              '';
          };
        }
      );
    };
}
