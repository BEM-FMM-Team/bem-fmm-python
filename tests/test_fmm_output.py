import ctypes

import pytest

import bemfmm.charge.fmm3d as fmm3d

_printf = ctypes.CDLL(None).printf
_printf.argtypes = [ctypes.c_char_p]
_printf.restype = ctypes.c_int


def test_native_fmm_output_filters_only_reallocation(monkeypatch, capfd):
    def fake_lfmm3d(*args, **kwargs):
        _printf(b" Reallocating\nFMM warning\n")
        return "result"

    monkeypatch.setattr(fmm3d, "_lfmm3d", fake_lfmm3d)

    assert fmm3d.lfmm3d() == "result"
    assert capfd.readouterr().out == "FMM warning\n"


def test_native_fmm_output_is_forwarded_if_fmm_raises(monkeypatch, capfd):
    def failing_lfmm3d(*args, **kwargs):
        _printf(b"Reallocating\nFMM error\n")
        raise RuntimeError("native failure")

    monkeypatch.setattr(fmm3d, "_lfmm3d", failing_lfmm3d)

    with pytest.raises(RuntimeError, match="native failure"):
        fmm3d.lfmm3d()
    assert capfd.readouterr().out == "FMM error\n"
