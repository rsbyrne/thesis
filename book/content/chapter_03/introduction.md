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

In the past, technology could be treated as the applied side of knowledge. Today, knowledge must increasingly be considered an application of technology.

While instrumentation has been integral to the scientific method since the time of Archimedes, the reliance of modern science on digital infrastructure has no real precedent short of the printing press. Software can slash the labour required to conduct almost any kind of numerical analysis. Remote sensing and online data have reduced the need for expensive and dangerous field work, while computational modelling has augmented or displaced many kinds of physical experimentation [@Heaton2015-wg]. Software and digital literacy have become non-negotiable requisites of a productive scientist's life, regardless of their interests or expertise.

+++

Science in the modern era is increasingly synonymous with scientific computing. Whether scraping social networks for data, analysing ever-growing databases of empirical results, training intuitive machines, reproducing nature in simulation, or even simply formatting a paper for publication, there would be very few scientists in the world today who have not found it necessary to develop at least some computing literacy [@Wilson2014-zo].

This revolution in the means of knowledge creation has arguably happened much faster than the adaptive timescale of the institutions it serves. Inefficiency, redundancy, and - all too often - the catastrophic loss of results, have all hampered the productive potential of this new technology. On the output level, new doctrines such as the FAIR program [@Wilkinson2016-qr] are beginning to address the issue of data persistence and access in principle, but are struggling in practice due to a worsening divergence of incompatible implementations [@Jacobsen2020-cc]. On the methodological level we find a proliferation of redundant solutions to related problems, a lack of reliable means of determining and disseminating best practices, and a state of alternating inability or unwillingness to absolutely require reproducibility after publication. Finally, on the most basic level, the skills portfolio of many workers is increasingly unequal to the challenges of devising, operating, managing, and packaging the ever-lengthening computational toolchains that best-in-field research now requires [@Wilson2017-xm].

With universities and scholars under pressure around the world, required to deliver more and more with less and less, it is clear that the engine of scientific progress is not sustainable in its present form. While new policies, better training, and stronger institutional supports all have a role to play in managing the symptoms of this pathology, the deeper cause is yet to be addressed. The scientific method today is simply too complicated for scientists. That is the challenge we must plainly recognise, and creatively overcome.

+++

In this chapter, we will first briefly sketch the problem at hand, then develop a formalisation of our approach to the problem; next, we will present our two research softwares: Everest, a general-purpose research data framework, and PlanetEngine, an Everest 'engine' built for our particular subject matter of planetary geodynamics; finally, we will show the code in action and discuss the future trajectory of the program.

```{code-cell} ipython3
##############################################################################
```
