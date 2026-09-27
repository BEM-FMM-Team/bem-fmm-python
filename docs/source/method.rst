Method
======

This page summarizes what the solvers compute. The references in the README
have the full derivations.

The model
---------

A head model is a set of closed, non intersecting surfaces, each with a
conductivity inside it and a known tissue outside it. The surfaces are merged
into one triangle mesh with N facets. Every facet knows its inside
conductivity :math:`\sigma_{in}`, its outside conductivity
:math:`\sigma_{out}` and its outward normal :math:`\mathbf{n}`.

At the frequencies of TMS and tDCS the fields are quasi-static. The total
electric field is a known primary field plus the field of charges that build up
on the tissue boundaries:

.. math::

    \mathbf{E} = \mathbf{E}_p + \mathbf{E}_s[\rho]

For TMS :math:`\mathbf{E}_p = -\partial \mathbf{A} / \partial t` is induced by
the coil current, for tDCS there is no primary field and the charges are driven
by the electrodes.

Charge on the boundaries
------------------------

The unknown is the surface charge density on each facet, stored divided by
:math:`\varepsilon_0` as :math:`c = \rho / \varepsilon_0` (units of V/m). A
charge layer makes the normal field jump by :math:`c` across the surface:

.. math::

    E_n^{in} = \bar{E}_n - \frac{c}{2}, \qquad E_n^{out} = \bar{E}_n + \frac{c}{2}

where :math:`\bar{E}_n` is the normal component of the total field at the
surface without the facet's own jump. No current may pile up at a boundary, so
:math:`\sigma_{in} E_n^{in} = \sigma_{out} E_n^{out}`. Solving for :math:`c`
with the contrast

.. math::

    \kappa = \frac{\sigma_{in} - \sigma_{out}}{\sigma_{in} + \sigma_{out}}

gives :math:`c = 2 \kappa \bar{E}_n`. Writing the field of the charges as an
integral operator :math:`K` over the whole mesh,
:math:`\bar{E}_n = E_{p,n} + K[c]`, this is a second kind integral equation:

.. math::

    c - 2 \kappa K[c] = 2 \kappa E_{p,n}

It is well conditioned, which is why GMRES needs only tens of iterations even
for close to a million facets.

Discretization
--------------

The charge is constant on each facet and the equation is enforced at the facet
centers. The field of all facets at all centers is a sum of about
:math:`N^2` point interactions, which the fast multipole method (FMM3D,
``lfmm3d``) evaluates in about :math:`N \log N` time. The point approximation
is poor for facets that are close together, so for the ``num_neighbors``
nearest facets of every facet the contribution is replaced by an accurate
integral over the facet. These corrections are a sparse matrix computed once
per model.

A small extra term, ``weight`` times the area weighted mean of :math:`c`, is
added to the equation. It keeps the total charge at zero, which the physics
requires but the discrete equation does not enforce by itself.

The system is solved with flexible GMRES until the relative residual is below
``relres`` or ``iter`` iterations are done. The residual history is stored with
the result and plotted in the Convergence tab.

TMS
---

The coil is a set of short straight current elements. For a current slope
:math:`dI/dt` the primary field is

.. math::

    \mathbf{E}_p(\mathbf{r}) = -\frac{\mu_0}{4\pi} \frac{dI}{dt}
    \sum_j \frac{\mathbf{s}_j}{|\mathbf{r} - \mathbf{r}_j|}

with :math:`\mathbf{s}_j` the vector of element :math:`j` and
:math:`\mathbf{r}_j` its center, again evaluated with the FMM. The right hand
side is the normal component at the facet centers. After the solve, the total
field at the facet centers is the primary field plus the field of the charges.

tDCS
----

Each electrode is a disk on the skin. Before solving, the skin mesh is cut
along the edge of every disk (imprinted) so that each electrode is an exact set
of facets. On the electrode facets the charge equation is replaced by a
condition on the potential,

.. math::

    \varphi(\mathbf{r}_i) = \frac{1}{4\pi} \int \frac{c(\mathbf{r}')}{|\mathbf{r}_i - \mathbf{r}'|} \, dA' = V_k

for every center :math:`\mathbf{r}_i` of electrode :math:`k`. The potential of
the ``num_neighbors_p`` nearest facets is integrated accurately. These rows are
very different from the rest, so each electrode gets a dense block
preconditioner (the potential interactions among its own facets, LU factored).
In place of the charge conservation term, ``weight`` times the normalized total
electrode current is added, which keeps the current going in equal to the
current going out.

After the solve:

- the current of electrode :math:`k` is
  :math:`I_k = -\sum_{i \in k} \sigma_{in} E_{n,i}^{in} A_i`, positive into the
  head
- the solved voltage is the area weighted mean potential over its facets
- the power is :math:`\sum_k V_k I_k`
- ``Jn`` is :math:`\sigma_{in} E_n^{in}` and ``Pot`` the surface potential on
  every facet

The sum of the currents should be close to zero. Its size relative to the
electrode currents is a quick check of a solve.

The uniform field check
-----------------------

``bemfmm sphere`` puts the three layer sphere in a uniform 1 V/m field. The
outermost layer faces air (:math:`\sigma_{out} = 0`), so the charges must cancel
the applied field everywhere inside. The field left inside is a measure of the
discretization error. The tests check it on random points.

E-field slices
--------------

A slice is the total field on a 200 x 200 grid covering the model in one plane,
evaluated with the FMM (plus the coil field for TMS), with the tissue outlines
where the plane cuts the surfaces. The colors use a log-modulus scale between
the smallest and largest field on the gray matter, so both weak and strong
regions stay readable.
