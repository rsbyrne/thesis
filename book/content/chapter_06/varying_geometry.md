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
