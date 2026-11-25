import ctypes
import os
import sys
import tempfile
from threading import RLock

from fmm3dpy import lfmm3d as _lfmm3d

_STDOUT_LOCK = RLock()


def _write_all(fd, data):
    remaining = memoryview(data)
    while remaining:
        written = os.write(fd, remaining)
        if not written:
            raise OSError("Could not forward native FMM output")
        remaining = remaining[written:]


def _flush_native_output():
    try:
        flush = ctypes.CDLL(None).fflush
    except (AttributeError, OSError):
        return
    flush.argtypes = [ctypes.c_void_p]
    flush.restype = ctypes.c_int
    flush(None)


def lfmm3d(*args, **kwargs):
    """Run FMM3D while filtering its known tree-growth notice from stdout."""
    # Redirecting fd 1 is process-wide, so serialize FMM calls around it.
    with _STDOUT_LOCK:
        try:
            saved_stdout = os.dup(1)
        except OSError:
            return _lfmm3d(*args, **kwargs)

        try:
            with tempfile.TemporaryFile(mode="w+b") as output:
                redirected = False
                try:
                    if sys.stdout is not None:
                        sys.stdout.flush()
                    os.dup2(output.fileno(), 1)
                    redirected = True
                    result = _lfmm3d(*args, **kwargs)
                finally:
                    try:
                        if redirected:
                            if sys.stdout is not None:
                                sys.stdout.flush()
                            _flush_native_output()
                    finally:
                        try:
                            if redirected:
                                os.dup2(saved_stdout, 1)
                        finally:
                            output.seek(0)
                            for line in output:
                                if line.strip() != b"Reallocating":
                                    _write_all(1, line)
            return result
        finally:
            os.close(saved_stdout)
