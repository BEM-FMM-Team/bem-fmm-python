Command line
============

Everything the program does is one command, ``bemfmm`` (or
``python -m bemfmm``). ``bemfmm <command> --help`` lists the options.

=================== ==================================================
``gui``             the graphical interface
``tms``             solve TMS for the coils in a setup, or the default coil
``tdcs``            solve tDCS for the electrodes in a setup, or the default montage
``slices``          E-field slices for a saved result
``show``            plot windows for a saved result
``sphere``          three layer sphere in a uniform field, a check of the engine
``export-matlab``   a tissue index as ``CombinedMesh.mat`` for the MATLAB scripts
``dipole``          primary field of a current dipole on a skull surface
=================== ==================================================

Solving
-------

::

    bemfmm tms                                  default coil on the default head
    bemfmm tms --setup setup.json               coils from a setup
    bemfmm tdcs --setup setup.json --tissue-index my_model/tissue_index.yaml
    bemfmm tdcs --relres 1e-3 --iter 30         a quicker, looser solve

Options shared by ``tms`` and ``tdcs``:

``--setup``
    Setup file from the gui. Without it ``tms`` uses the default coil and
    ``tdcs`` the default four electrode montage.
``--tissue-index``
    Model to solve on. Defaults to the index named in the setup, then to the
    default head.
``--num-neighbors``, ``--iter``, ``--relres``, ``--weight``
    Solver settings, see the Solve tab in :doc:`gui`.
``--output-dir``
    Where ``result.json`` and ``result.npz`` go, ``./__output__`` by default.
``--save-format`` and ``--save`` / ``-s``
    Also write single fields, for example ``--save-format mat -s E -s En``.
``--slices``
    Also compute the E-field slices and save them as ``slices.npz``.
``--plot`` / ``--no-plot``
    Open the plot windows when done, ``--plot-tissue`` picks the tissue.

``tdcs`` also has

``--skin``
    Tissue the electrodes are imprinted on. Defaults to the Place on surface
    stored in the setup, then to ``skin``.
``--num-neighbors-p``
    Facets integrated exactly for the potential on the electrodes.

After a solve ``tdcs`` prints a table of the set and solved voltage and the
current of every electrode, with the current balance and power. A setup with
fewer than two electrodes, or with all of them at the same voltage, stops with
an error before the model is loaded.

Slices
------

::

    bemfmm slices __output__                    at the planes of the saved setup
    bemfmm slices run01 --planes 30 -12 54      axis planes through x, y, z in mm
    bemfmm slices run01 --plane 1,-1,0,0,0,0 --plane 0,0,1,0,0,20

``--plane`` is one plane by its normal and a point on it in mm, six numbers
separated by commas, and can be given more than once. The example is the plane
y = x and the plane z = 20 mm. Without ``--plane`` or ``--planes`` the planes
come from the run's ``setup.json``, else the axis planes through the point where
the coil axis meets the white matter (TMS) or through the origin (tDCS).

The slices are saved next to the result as ``slices.npz`` and are shown by the
gui and by ``bemfmm show``. They take a few seconds on the sphere and about a
minute on the full head. TMS slices include the primary field of the coils.

Other commands
--------------

::

    bemfmm show __output__                      plot windows for a result
    bemfmm show run01 --plot-tissue gm
    bemfmm sphere                               uniform field on the sphere
    bemfmm export-matlab --tissue-index my_model/tissue_index.yaml --out CombinedMesh.mat

Caching
-------

The expensive parts of a solve (neighbor integrals, the charge solution) are
cached in ``__compute_cache__`` in the repository, keyed on their inputs. A
repeated run with the same model and coils or electrodes is much faster. Delete
the folder to clear the cache, or set ``BEMFMM_NO_CACHE=1`` to turn it off.
