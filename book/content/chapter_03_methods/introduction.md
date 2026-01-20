---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.0
kernelspec:
  name: python3
  display_name: Python 3 (ipykernel)
  language: python
---

```{code-cell} ipython3
##############################################################################
```

In Western military theory, there is a maxim: "Quantity has a quality all its own."

In the natural sciences, this maxim has a double-edged truth. Quantity - of observations, of experiments, of models - opens up new frontiers of discovery: not greater per se, but profoundly different to the frontiers of 'small-run' science. At the same time, quantity creates new technical challenges: again, not necessarily greater, but fundamentally different to the challenges of executing a narrowly-focussed study.

To the old maxim, we might add a corollary: "And different quantities may have different qualities too." In other words, not all forms of "big" science are created equally. The 2010s saw a boom in 'Big Data'. The promises made at that time were as sweeping and ecstatic as those attending today's AI boom. In many cases, however, the promised transformations were abortive, underwhelming, or simply not forthcoming.

Moving between scales successfully requires understanding what properties are preserved, lost, and changed in the scaling. It requires tools that are responsive to the unique qualities of working at a particular scale, and an appropriate mentality on the part of the scientist to recognise the costs and pursue the novel benefits on offer.

Geodynamics has always been at the vanguard of new methodologies, embracing numerical modelling, Big Data, and now AI, with energy and felicity. This thesis aims to contribute to that legacy by exploring the potential of highly object-oriented approaches to open up new ways to 'go big' on the model frontier.

At its simplest, this thesis is committed to exploring the potential benefits of a simple tradeoff between two kinds of 'quantity': lower resolution (quantity of calculations per model) in exchange for richer parameter space coverage (quantity of cases sampled). It will be shown how the journey from small-batch modelling to big-batch and, finally, truly massive suite-modelling, has entailed radically new approaches to designing, managing, shepherding, storing, organising, analysing, visualising, and even conceptualising big model runs for the big computing age - and not just for geodynamics, but for any field targeting similar 'shaped' problems.

In this chapter, we will first briefly sketch the problem at hand, then develop a formalisation of our approach to the problem; next, we will present our two research softwares: Everest, a general-purpose research data framework, and PlanetEngine, an Everest 'engine' built for our particular subject matter of planetary geodynamics; finally, we will show the code in action and discuss the future trajectory of the program.

```{code-cell} ipython3
##############################################################################
```

Scraps

The downside of being in the vanguard - to continue the military metaphor - is that one is invariably among the first to crash into unforeseen obstacles: often painfully. The wider world has been the beneficiary of planetary scientists' willingness to commit substantial resources to deep methodological innovation: particle-in-cell methods, inverse modelling, and Krige-type interpolation are all owed to the field.
