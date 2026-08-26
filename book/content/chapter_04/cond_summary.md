**Common expressions**:

$$ \begin{align*}
r_i &= \frac{f}{1 - f} \\
r_o &= \frac{1}{1 - f} \\
r_m &= \frac{r_{i} + r_{o}}{2} \\
r(h) &= r_i + h \\
{r^*}(h) &= \frac{r(h)}{r_o} \\
s^*(h) &= \frac{r(h)}{r_m} \\
\mathrm{Disc}(h) &= \frac{r(h)^2 - {r_i}^2}{2r_m} \\
W(z) &= \text{Lambert W function satisfying } z = W(z)e^{W(z)}
\end{align*} $$

+++ {"editable": true, "slideshow": {"slide_type": ""}}

**Conductive equilibrium temperature profiles ($0 \le h \le 1$)**:

Basal heating in the Cartesian ($f \rightarrow 1$, $H=0$):

$$ \begin{align*}
T''(h) &= 0 \\
T'(h) &= -1 \\
T(h) &= 1-h \\
T_\mathrm{av} &= \frac{1}{2}
\end{align*} $$

Internal heating in the Cartesian ($f \rightarrow 1$, $H \gt 0$, insulating base):

$$ \begin{align*}
T''(h) &= -H \\
T'(h) &= -H\cdot h \\
{T(h)} &= H \frac{1 - h^2}{2} \\
T_\mathrm{av} &= \frac{H}{3}
\end{align*} $$

Mixed heating in the Cartesian ($f \rightarrow 1$, $H \ge 0$):

$$ \begin{align*}
T''(h) &= -H \\
T'(h) &= -H \left( h - \frac{1}{2} \right) - 1 \\
T(h) &= H \frac{h \left( 1 - h \right)}{2} - h + 1 \\
T_\mathrm{av} &= \frac{H}{12} + \frac{1}{2} \\
\end{align*} $$

Basal heating in the annulus ($0 < f < 1$, $H=0$):

$$ \begin{align*}
T''(h) &= -\frac{1}{r(h)^2 \ln f} \\
T'(h) &= \frac{1} {r(h) \ln{f} } \\
T(h) &= \log_f r^*(h) \\
T_{\mathrm{av}} &= \frac{1}{2} \left(-\frac{1}{\ln f} - \frac{{r_i}^2}{r_m} \right)
\end{align*} $$

Internal heating in the annulus ($0 < f < 1$, $H \gt 0$, insulating base):

$$ \begin{align*}
T''(h) &= H_\mathrm{coeff} \; {T_\mathrm{basal}}''(h) - \frac{H}{2} \\
T'(h) &= H_\mathrm{coeff} \; {T_\mathrm{basal}}'(h) - \frac{H}{2}r(h) \\
T(h) &= H_\mathrm{coeff} \; T_\mathrm{basal}(h) - \frac{H}{4} \left( r(h)^2 - {r_o}^2 \right) \\
T_\mathrm{av} &= H_\mathrm{coeff} \; T_\mathrm{av, basal} + \frac{H}{4} r_m \\
&\text{where} \quad H_\mathrm{coeff} = \frac{H}{2} {r_i}^2 \ln f
\end{align*} $$

Mixed heating in the annulus ($0 < f < 1$, $H \ge 0$):

$$ \begin{align*}
T''(h) &= H_\mathrm{coeff} \; {T_\mathrm{basal}}''(h) - \frac{H}{2} \\
T'(h) &= H_\mathrm{coeff} \; {T_\mathrm{basal}}'(h) - \frac{H}{2}r(h) \\
T(h) &= H_\mathrm{coeff} \; T_\mathrm{basal}(h) - \frac{H}{4} \left( r(h)^2 - {r_o}^2 \right) \\
T_\mathrm{av} &= H_\mathrm{coeff} \; T_\mathrm{av, basal} + \frac{H}{4} r_m \\
&\text{where} \quad H_\mathrm{coeff} = 1 - \frac{H}{2}r_m
\end{align*} $$

+++

**Inverse temperature profiles ($0 \le h \le 1$)**:

Basal heating in the Cartesian ($f \rightarrow 1$, $H=0$):

$$ \begin{align*}
h(T) &= 1 - T
\end{align*} $$

Internal heating in the Cartesian ($f \rightarrow 1$, $H \gt 0$, insulating base):

$$ \begin{align*}
h(T) &= \sqrt{1 - \frac{2T}{H}}
\end{align*} $$

Mixed heating in the Cartesian ($f \rightarrow 1$, $H \ge 0$):

$$ \begin{align*}
h(T) &= \frac{H - 2 + \sqrt{(H+2)^2 - 8HT}}{2H}
\end{align*} $$

Basal heating in the annulus ($0 < f < 1$, $H=0$):

$$ \begin{align*}
h(T) &= \frac{f^T - f}{1 - f}
\end{align*} $$

Internal heating in the annulus ($0 < f < 1$, $H \gt 0$, insulating base):

$$ \begin{align*}
h(T) &= \frac{x(T) - f}{1 - f} \\
&\text{where} \quad x(T) = \sqrt{ -f^2 W\left( -f^{-2} \exp\left( -f^{-2} + \frac{4T}{H {r_i}^2} \right) \right) }
\end{align*} $$

Mixed heating in the annulus ($0 < f < 1$, $H \ge 0$):

$$ \begin{align*}
h(T) &= \frac{x(T) - f}{1 - f} \\
&\text{where} \quad x(T) = \sqrt{ \frac{A}{2B} W\left( \frac{2B}{A} \exp\left( \frac{2(T-C)}{A} \right) \right) } \\
&\text{where} \quad A = \frac{1 - \frac{H}{2}r_m}{\ln f}, \; B = -\frac{H {r_o}^2}{4}, \; C = \frac{H {r_o}^2}{4}
\end{align*} $$