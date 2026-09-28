#!/usr/bin/env bash
# run.command without the 3D view, for remote sessions without OpenGL
exec "$(dirname "${BASH_SOURCE[0]}")/run.command" --no-3d "$@"
