---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.5
kernelspec:
  name: python3
  display_name: Python 3 (ipykernel)
  language: python
---

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
---
import aliases # important this goes first to configure PATH

from everest.window import image, imop
from everest.window import Canvas, DataChannel as Channel
from everest.window.colourmaps import cmap

import PIL
import os

aliases.limit_memory(8.0)
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

# Varying geometry

+++ {"editable": true, "slideshow": {"slide_type": ""}}

*Note to supervisors: The material here is mostly adapted from my COSPAR talk; again, there is more data and analysis on all of this, and it's just about identifying the most important figures to tell the story. I haven't had time to adapt my notes into 'thesis voice', so apologies for the lack of prose here. I had a voice model make a transcript of my COSPAR talk - I've pasted it here as a placeholder, partially to provide some extra context on the content, and partially because it's hilarious (keep an eye out for the Moray's Insult of 1998).*

+++ {"editable": true, "slideshow": {"slide_type": ""}}

## COSPAR transcript (not very good!)

Hi there, everyone. We're here to talk about episodic overturn on Venus. So my name is Rowan Byrne. I come from the underworld team. And we are a team of numerical geodynamic modelers based on a variety of universities, especially in Australia, with friends and affiliates and users all over the world. So this is me over here in the School of Earth Sciences. If you're ever in Melbourne, come say hi. And my supervisor is Lou Morese, who many of you will recognize, and Rebecca Farrington, who's our laboratory manager as well. So what we do is computational geodynamics using Underworld, which is an open source, particle and cell finite element fluid modeling code. It's powered by PET-C, but it has a really flexible Python wrapper that allows you to do lots of fun things, as we'll see. And we model the solid earth and basin scale to mantle scale. And my particular focus is planetary organization, planetary destiny, why are planets as they are? Is it to do with their big numbers, the mass radius insulation, or is it to do with small numbers, the configuration of the system, where the hot areas are, where different rock types are, that sort of thing? We are modeling the planet scale convection all the way through geological time. exploring lots of different counterfactuals and hypotheticals, as well as the historical values that we're all familiar with. And in particular, for my thesis on evaluating the role of lithospheric heterogeneities, particularly, you know, you're looking at continents, proto-continents, oceanic plateau, that sort of thing, which might have changed the parameter space, you know, changed the phase space of the early Earth and made plate tectonics possible here in a way that it wasn't elsewhere. So here is our old model. It's the Moray's Insult of 1998. It's the classic, we've all seen it. An employee was then a brand new branching viscoplastic biology where there's a yield strength criterion that toggles between a exponentially temperature dependent viscosity and a purely stress dependent viscosity. It's the first non-trivial tectonic mode to be discovered beyond plate tectonics. So as old as the model is, it remains a really important one. and a constant touchstone for people in our field. This paper gets cited all the time, even today. And this is from the original paper. You can see his three end members, the mobile end member, the stagnant end member, and then in between episodic overturn. So he's had to go at the drawing up a phase diagram of the system, but they didn't have very many models they were able to run at the time, just due to resource limitations. Now, the issue, of course, is that Venus is not what it used to be. There's a growing awareness that it remains complex and active. It's not actually being key essence for 200 million years at a time. There are multiple and diverse hints of ongoing volcanism, those coronary, maybe active structures, and there's some evidence of plume tectonics as well. So I figured it would be a good idea to revisit this classic. It remains a benchmark, but it's never actually been thoroughly revisited on its own terms, but with modern resources. So the sampling wasn't very dense. There was a limited exploration of the effect of varying model geometry, very short runtimes and so on. For a massively and perpetually sided bell weather paper, I think we can do that. So here's the code it's bound by underworld with a few flourishes of my own that I'm very happy to talk about. It's all open access online and my code is due for a formal release soon. So it looks something like that. Actually the syntax is a bit more elegant than this these days. And the models themselves look something like this. So this is a curved model with a two to one aspect ratio. You can see the, where it's yielding at the top where these viscosity contours have started to come together. And this is a sinusoidal initial perturbation of one, which is what I predominantly use during my modeling, sorry, perturbation of two. The idea is that it's an interface that reads the way that a good modeler thinks. At least the way that I think the good modelers think. So here's the data, and it's a lot of data. So it was a mesh-based finite element viscous fluid model. We had a lot of parameters, but the input parameters we're really looking at here are the yield strength to our RAF, the aspect ratio, and the curvature F defined as the ratio of the outer and lower mantle lengths. And we collected a lot of outputs, 30 different channels of outputs, complete model data for many, many of the steps, but also even more frequent collections of lots of analytical reduction data, especially the Nusselt number, the velocity of it being square, and the yield fraction, which we'll be talking about today. It's a growing data set, as I said. It's already thousands of models long. And, oh, pardon me. It's already thousands of models long. And it's getting bigger every single day. with hundreds of models cooking as we speak. It's a lot of CPU hours, if you were to book them on the open market, but actually it doesn't take that much computation to get here. The main reason this work hasn't been done, in my opinion, is that it's been inconvenient, but I have tools that make it a lot easier now. And I think that there's a lot of low hanging fruit here. Let's have a look. Obviously the original paper reproduces perfectly, as you'd expect from my supervisor, Merezi. the mobile end member, the statement end member, and the episodic regimes in between. And you can see here in the gifts, roughly what they look like. So there's your stagnant lid. There's what your mobile lid looks like. And here's the episodic overturn where the lid is mobilized for brief periods every now and then. These failure events all have the same profile. So every failure is the same event, no matter what parameters you're using for the model. It always looks the same. However, that's where the similarities stop between different cases. Actually, every case has a different frequency of failures. And if you use a noisy initial condition, as I have here, you start to get modes that certainly weren't tested in the original paper. In this case, we get these twinned failure events that are stable at a very long time scale. quite compelling to me. So here's a full reproduction of the same geometry in the original paper, this time using a sinusoidal initial condition, whereas the original paper used an isobiscus initial condition. This one here is sinusoidal because it's a bit more flexible for comparison to allow it to be varied systematically to explore the effects of different initial conditions. It broadly gets to the same place as the pure reproduction I just showed you. Here's your mobile and member. Here's your stagnant and member. And here are all the episodic regimes in between. The one episodic regime with many, many different ways of manifesting, primarily differing by the amplitude of the failure events and the frequency of them. And we see the same thing as the original paper that there are these three modes, and you can identify them very clearly where the boundaries are. But there is systematic variation within especially the episodic mode. I've checked up the velocities here as well. I think these are quite interesting. You see that as yield strength increases, obviously the surface velocity just orange here completely drops to nothing because it's stagnant, a definition. But actually the velocity root mean square of the model as a whole increases with increasing your strain. Because the thickening of the upper boundary layer for a model of aspect one geometry actually pushes the sub lithospheric mantle to an aspect ratio that allows for more efficient convection. And that's very interesting. And we'll see the effect of that in a moment. If you take a Fourier analysis of those Nusselt profiles I showed you before, You can see, again, these three different regimes, but there's systematic variation within the Fourier regime. And you can see, in particular, these dominant frequencies are changing over time, sorry, are changing with respect to different yield strengths, as you can see here. Now, if we take these models, and if we take the sinusoidal frequency one models, and then we compare those to the same models with the same parameters, but with a different initial condition, of double the initial sinusoidal perturbation, then we actually get the same behavior at the stagnant end of phase space, but we get very different behavior at the mobile end. So actually at the mobile end, having a more active initial condition allows the model to stabilize in the episodic regime, even at values of yield strength, where we wouldn't think it was possible. So that's an early clue that there's a lot more going on than we might think. So the other thing I did, of course, was explore the effective geometry. As I said, here's increasing aspect ratio. So wider models, here's more curved models where 0.5 is Earth-like curvature and 1.0 is like a perfectly square box. And generally, we see that increasing the length of the outer boundary layer in the sense of increasing the curvature or increasing the aspect ratio or both has the effect of referencing the mobile regime and effectively weakens the upper lithosphere compared to the convective vigor. And that's quite interesting in itself. If you have a sort of closer look at the effect of this curvature, you're seeing that the varying curvature actually moves the entire envelope of the episodic overturn regime who different values of are not. And it actually moves the stagnant end as well as moving the mobile end, whereas varying the initial condition only move the mobile end. So actually the point where planets can stagnate is completely different depending on what the effective thickness of the convecting mantle is because curvature is a proxy for effective mantle convection thickness or core ratio is the same thing. So these two populations we see are greater than 0.75 curvature and less than 0.75 curvature. And if you go to a wider aspect ratio, pardon me, this is a typo. This is now aspect 1.4 and 4, square root 2, we know from our basic geodynamics that this should be a more efficient plan form or enable a more efficient plan form in an isoviscus model. And again, we see that it's completely altered the envelope where episodic overturn occurs. So episodic overturn, the Bayes diagram of this model is very dependent on the geometry of the model. Now, if we look at this in a bit more detail, you can fit a regression curve to the dominant frequencies, so essentially the frequency of these major failure events. you plot these on the y-axis, you plot these against your parameter of yield strength on the x-axis, and you can fit a straight line, although this is a log graph, but take my word for it, that this is a straight line with a very high confidence. So that actually the frequency is almost, it appears to be almost solely linearly dependent on the yield strength acuping the geometry constant, which is quite compelling because it explains why the lid mobilizes when it does. If you take one over this frequency, you get a dimensionless time that is pretty similar to the time it takes to recover from one of these failure events. So this has been a narrative that when the frequency has become too, when the family has become too frequent for the, it's become so frequent, pardon me, that the failure events actually overlap in a sense. And then this episodic behavior collapses and you get a stable mobile lid. The stagnant end is a little bit more mysterious as we'll see. And so we have some sort of linear relationship here where we have these hyper parameters of A and B. And interpreting these is, will be the subject of my thesis. It's a very interesting challenge. B is some sort of reference where it can see and A has the units of time per length, which is very suggestive. Now, if we vary the curvature, then we see that the parameters of this regression that we're fitting through the frequencies also changes and changes systematically. And again, we see these two populations less than 0.75 curvature, greater than 0.75 curvature that have different hyperparameters. So we have now curvature as another linear coefficient of the frequency-towel relationship. But A, but this, hyperparameter A takes different values depending on whether you are below 0.75 or above 0.75. In other words, there's a purely geometric transition, which is something that might be very influential in real planets. If you think about the changing effective mental, changing effective, convecting mental thickness as a result of say cooling from the bottom or cooling from the top, that at one point there's a discrete geometric forced transition between two different laws that could govern the system. We might be seeing that in fact all over the place. So that's quite provocative. So that's all I have time to show you today. As I said, it's a massive data set. We're just scratching the beginning. And I invite anyone to jump in and help me really take this thing apart. It's hundreds of gigabytes. It's thousands of bottles. And it's a lot of fun to get into. Thank you, big picture. My goal is to make this Moravian Solon Top Model with a few more parameters to make it a bit more useful. But essentially to make this model a sort of Drosophilia fly genome model that would be to us what the fly genome is to a real sort of bellwether a touchstone something that we understand so well, we don't have to go back and model it. We can just refer to our analytical understanding of the drive from the modeling. I think we have a very good chance of doing that. And I think I've had a pretty good. Um, introductions as well. It's a huge data set. So that obviously means it's amenable to big data approaches. This is just a pure linear regression model. That's essentially, uh, the simplest possible, uh, learning model you could think of, but with 35 different parameters. And already it's able to capture the n members and some sense of the episodicity in between those n members. So imagine what we can do with a more sophisticated neural net being applied to this data set with so many different channels that are all correlated. It's perfect for that sort of application. I also collect these rasters of the data that are always the same format, no matter what the geometry or physics of the model is. So this immediately makes it amenable to off-the-shelf image recognition libraries. and things like clustering, algorithms, exploratory factor analysis, all the stuff that we're very familiar with from big data. Now that we have a very, very large data set with thousands of cases varying very finely over certain parameters, there's a lot of knowledge that we could extract from these models, a lot of insights using those sorts of techniques. It's low hanging fruit, it's easy to do. It's what I'm gonna be doing for the next many years. And I invite everyone else, as I said, to jump in be a part of the team and to help us really take this apart, figure out what's going on with this model that could be really the first completely understood non-trivial model. So that's all. I welcome any questions and correspondences from all in Sundry. That's all for me. Take care and

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: cospar_image37
tags: [remove-cell]
---
# cospar_image37

image.fromfile(aliases.storagepath / "cospar_figs" / "image37.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #cospar_image37
:name: cospar_image37_fig

*Nusselt* timeseries data for varying aspect ratio and curvature. Increasing $f$ and aspect both have the effect of increasing the convective flux for a given value of yield strength while also reducing the amplitude and frequency of failure events. Endmember crustal thicknesses, however, are largely unaffected.
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: cospar_image26
tags: [remove-cell]
---
# cospar_image26

image.fromfile(aliases.storagepath / "cospar_figs" / "image26.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #cospar_image26
:name: cospar_image26_fig

Key observation channels for varying curvature parameter $f$.
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: cospar_image29
tags: [remove-cell]
---
# cospar_image29

image.fromfile(aliases.storagepath / "cospar_figs" / "image29.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #cospar_image29
:name: cospar_image29_fig

Key observation channels for varying curvature parameter $f$ at aspect ratio $\sqrt{2}$.
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: cospar_image30
tags: [remove-cell]
---
# cospar_image30

image.fromfile(aliases.storagepath / "cospar_figs" / "image30.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #cospar_image30
:name: cospar_image30_fig

Dominant frequency as a function of yield strength for varying curvature. By observing how the regression parameters change with respect to the model parameters, we can gain some clues about their nature and dependencies. It is immediately clear that lowering the curvature parameter (i.e. lengthening the upper boundary relative to the lower boundary) systematically steepens the dependency of frequency on yield strength.
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: cospar_image46
tags: [remove-cell]
---
# cospar_image46

image.fromfile(aliases.storagepath / "cospar_figs" / "image46.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #cospar_image46
:name: cospar_image46_fig

Meta-regression analysis suggests $f$ (curvature) is a linear coefficient of the episodic overturn regression parameters: $n=a\,f\left(\tau+b\right)$, where the $a$ parameter now takes on two distinct values above and below a transition point around $f = 0.75$. In short, there is apparently a purely geometric mode transition inside the viscoplastic regime.
```
