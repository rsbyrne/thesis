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

---
math:
  '\R': '\mathbb{R}'
  '\vector': '\boldsymbol{#1}'
  '\der': '\frac{d#1}{d#2}'
  '\cursor': '\mathinner{\color{darkgray}{\mathrm{I}}}'
---

+++

# SCRAPS


#### Unpacking containers

The unpacking operator has a second function, equal in significance to the first: when applied to containers, ``*`` returns a single value which is conceptually a 'superposition' of all the container's members.

In the (presumptive) default environment, containers with zero members resolve to ``undefined`` on unpacking, and containers with exactly one member simply return that member.

Containers with more than one member are handled in a manner that depends on the environment that the program is being executed in, but conceptually involve some form of branching behaviour. That behaviour could include soliciting user input - e.g. ``*(+'Yes' | +'No')``; alternatively, one could implement a non-deterministic executor that explores many possibilities. For environments without 'branch handling', the fallback behaviour is to return ``undefined``.

Container unpacking provides an easy means to build finite arbitrary mappings - i.e. 'dictionaries'. Consider:

```
*(+(0=a) | +(1=b)).0 == a ? 'Just like a dictionary!'
```

This snippet builds a container of maplets where the 'key' of each maplet is a unique integer. This guarantees that the result of any valid query will be a singleton set, which `*` then unpacks, returning the desired result.


#### The unpacking stack

When a lazy expression is scheduled for unpacking, a pair of dedicated stacks is created: an 'input' stack and an 'output' stack. Every `*` symbol is associated with such a pair, and a pair of special operators are reserved specifically for interacting with them: the nullary 'pop' operator ``_``, which pulls the next item off the input stack and evaluates to that value (or ``undefined`` if the stack is empty), and the unary prefix 'push' operator ``^``, which pushes its operand onto the output stack while itself evaluating to ``undefined``.

By default, the input stack is empty. 



Here is a very simple example of `^` and `_` in action:

```
!expr=`(^2; _);
*$expr == 2 ? 'The value was pushed, then popped, then returned.'
```

Note that, even though all four sub-expressions inside ``expr`` were technically equally 'engraved', they all shared the same stack, because they were all unpacked by the same instance of ``*``. If it is instead desirable to evaluate part of the expression in the context of its own stack, this can be achieved with an internal, graved ``*``:

```
!expr=`(*`^2; _);
*$expr; 'The result was undefined because 2 was pushed to the inner stack.'
```

Given that every Gospel program is itself simply an expression, which is implicitly unpacked by a single 'entry unpacker' throughout the course of program execution, 'top-level' instances of `_` and `^` function can be expected to behave in exactly the same way as they do inside explicit unpackings. They do indeed, but the 'stack' upon which they act resides in the user domain; thus `_` at the top level is analogous to 'retrieve the next program argument' and `^` at the top level is analogous to 'return this value as output'.

#### Packing the stack

+++

### The Parsimon Algorithm

+++

It turns out that this problem, stated a little differently, is well-known, and its solution is surprisingly simple. In principle, what we have is a kind of 'optimal transport' problem - often dubbed the 'earth moving' problem in computer science. The classical framing of the problem imagines a pile of dirt that must be moved to another pile at a minimal 'cost', where the cost is the amount of earth to be moved times the distance that it has to be moved. The problem was posed and solved in the context of actual earth-moving problems in the early 20th century.

The solution to the 'earth moving' problem, as it transpires, is not complicated, even for our infinite sets. We simply need to sort the contents of each Noum from highest component to the lowest component (with the hidden tail of Voids conceptually extending infinitely thereafter), then allocate the dimensions from left to right. The resulting dimensionalisation has the unique property that the Euclidean distance between every pair of points is the minimum it can be, and therefore the set as a whole is minimally spread (we say that the "earth mover's distance" has been minimised).

This algorithm is obviously efficacious for our trivial example (because $A$ and $B$ are identical when their components are aligned), but it works in the same way and for the same reason for any set of Noums where all the Noums have the same cardinality (i.e. they can lined up component-for-component). Since all our Noums have the same cardinality by definition (because every Noum has exactly one value for every Pleroma dimension), we are always able to line them up efficiently so long as we go in descending order.

We can even accommodate negative components by taking their absolute value before sorting; if we keep track of which components were previously negative, we can account for that in the sort and ensure that the ordering remains unique (up to an equivalence); we will simply declare that 'formerly negative' components go *after* any components that they now happen to be equal to after taking the absolute.

| $A = \lgroup -1. 0, 1, 100 \rgroup$ | $B =\lgroup 0, 0, 1, 1, 100 \rgroup$ | Dimension | Values |
| - | - | - | - |
| $100$ | $100$ | x | $A=100$, $B=100$ |
| $1$ | $1$ | y | $A=1$, $B=1$ |
| $\lvert -1 \rvert = 1$ | $1$ | z | $A=-1$, $B=1$ |
| $0$ | $0$ | u | $A=0$, $B=0$ |
| $-$ | $0$ | v | $A=\mathrm{Void}$, $B=0$ |

A set of Noums articulated for the sole purpose of 'conjuring up' dimensions from the Pleroma shall be termed a 'Base Set'. The dimensions made available by a given Base Set $B$ shall be termed the "dimensions of $B$ under parsimony".

Defining a good Base Set is the first step toward structuring the Pleroma for practical use.

+++

## Schemas and symmetries

+++

### Hyperreal tagging

+++

The examples we used to demonstrate the Parsimony Algorithm were totally arbitrary - and in fact, not valid as Noums (the intervals should be limited to $(-1, 1)$). Ideally, we would prefer for the Base Set to vanish as soon as we have our dimensions, but this is not possible: without the Base Set, the referenced dimensions become inaccessible once again and we are back at square one. It seems we need to define a Base Set that is persistent, but negligible, so that it doesn't 'contaminate' any structures that may later be built on top of it.

Simultaneously, we need a way to create actual 'data Noums' (arbitrary Noums intended to represent things) that can 'attach' to the dimensions referenced by the Base Set. We can't rely on parsimony to supply these dimensions because the assumption of parsimony - i.e. that the vectors are maximally clustered - is antithetical to

+++

### Scaffolds

+++

Now that we have acquired the ability to assign

+++

The object in which a Pleroma is associated with a Scaffold clearly has many potentialities which the Pleroma by itself lacks. This new object we will term a 'Cosmos'. Because the Scaffold, by ordering all points, necessarily

+++

### Scaffolds

We just introduced the idea of using an 'eight-space' to store an eight-bit integer. This presupposes that the dimensions are ordered, but in the Pleroma as we have defined it, this is not so - at least, not by default.

Countably infinite structures permit all sorts of operations that uncountable structures do not - like Hilbert's trick to obtain finite distances across infinite dimensions. Unfortunately, this sort of maneouvre also requires the dimensions to be structured in some way so that an algorithm can visit them discretely and act on them distinctly. Hilbert structured his dimensions simply by numbering them from $1$ to infinity. We do not have the luxury of pre-structuring the Pleroma like this, firstly because our dimensions represent concepts which are not universally ordered, and secondly because any particular choice of structure would prejudice against other equally tractable structures that may not be homeomorphic to it.

Instead, we must provide a framework for structures that is strict enough to permit analysis and interoperability while also being flexible enough to accommodate all uses cases and semantic interpretations.

Let us therefore introduce the concept of the 'Scaffold'. A Scaffold is a 'structure over dimensions', so-called because it makes the Pleroma accessible without changing its content. Strictly, a Scaffold is a function that receives the standard form of any two points $a$ and $b$ in the Pleroma and returns a hyperreal number in the open symmetric unit interval, $V$, giving the 'provisional ordering' of the two points 'under the Scaffold':

| Result | Interpretation |
| --- | --- |
| $\mathrm{st}(V) > 0 $ | $a$ is provisionally greater than $b$ |
| $\mathrm{st}(V) < 0 $ | $a$ is provisionally lesser than $b$ |
| $\mathrm{st}(V) = 0 $ | $a$ is provisionally equal to $b$ |
| $V = 0 $ | $a$ is provisionally incomparable to $b$ |

The Scaffold relation is further held to the following criteria:

1. There must be a valid $V$ for every pair $a$ and $b$.
2. There shall only ever be a countably infinite number of points that are 'equal', order-wise, to any given point.
3. A pair that is deemed to have an ordering in one direction has the inverse ordering when the pair is reversed (i.e. the relation is transitive).
4. The 'universal origin' (the point whose standard part is zero in every dimension) is comparable to every point (i.e. is always greater than, lesser than, or equal to any other given point).

Like any binary relation that permits equivalence, Scaffolds effectively 'partition' the set into what are called 'equivalence classes'. Thus our second criterion can be more succinctly stated as: *There shall be no uncountable equivalence classes*. If the union of all equivalence classes must include every point in the Pleroma (as required by the first criterion), and the classes themselves are only countably finite, then it is further implied that there must be an uncountably infinite number of classes - otherwise points would necessarily be 'left out'.

Binary relations of this form (where values can be greater than, lesser than, equal to, or incomparable with each other) generate what are called 'partially ordered sets'. In the case of our Scaffold, the Pleroma is broken up into an infinite collection of 'bags' where each bag can hold a vast but not uncountable number of Pleroma coordinates which have evaluated to 'provisionally equal' with each other. We can imagine labelling the bag itself with this value for ease of comparison with other bags; immediately we will see that no two bags are labelled the same (otherwise they would have been merged) but some bags have labels that cannot be directly compared with each other. Consequently the bags themselves form the nodes of a directed acyclic graph (a 'DAG'), with one or more 'least' nodes (i.e. nodes where no node is strictly 'lesser'), one or more 'most' nodes (i.e. nodes where no node is strictly 'greater'), and a lattice of zero or more nodes floating around inbetween.

+++

What we need is a way of extracting symmetries from data that - when represented as data inside the system's epistemic substrate - captures something real about the outside world: a microcosm to match the macrocosm.

This, finally, is where models come back in.

+++

When we bring a particular logos under study, what we are typically looking for is planes of symmetry that are comparable in complexity to the Schema itself. In mathematics, these are called 'theorems'; in machine learning, 'features'. We shall use the term 'Modes', with its statistical, physical, and musical overtones.

+++

The society of science - 'The Academy', as it is sometimes called - is of course not just an information system, but aspires to be a true knowledge system: the largest ever constructed. Yet, while knowledge-making is second nature to individual humans, it is not granted that a society will respond to information in an epistemic way. The Academy has evolved many organs to ensure its continuation as a true knowledge system: a bespoke genre of non-fiction literature (peer-reviewed journals), a hierarchical social structure (undergraduates, graduates, and faculty), an enforceable code of conduct (scientific ethics), a body of standard practices (scientific method), and a family of ritual dialects (jargon), to name a few. But the pressures of the machine age threaten to strain and even overwhelm these systems.

To build knowledge systems that are capacious enough, responsive enough, and resilient enough for the 21st century, we must rebuild the science stack from the ground up. We contend that the foundation stone of the new science must be modelling.

+++

This is similar to, but somewhat weaker than, requiring a 'metric' that gives the distance between any two points, since any such system can be used to order all points by distance from the origin. The looser constraint allows more kinds of structures to qualify as Scaffolds, while still ensuring that two different Scaffolds with two different 'opinions' about ordering can always enter into a relation with each other through a point-for-point comparison.

```{code-cell} ipython3
##############################################################################
```

### Structuring the pleroma

+++

The purpose of this entire enterprise is to develop a coherent, complete, and convenient framework for building, operating, and analysing functional knowledge systems.

So far, we have introduced information systems, and we have shown how information systems can be endowed with Schemas to elevate them into data systems. However, we deliberately resisted characterising data as knowledge and instead committed lengthy passages to discussing various techniques that can be applied to Schematic data.

We stated earlier that knowledge, in our framework, is a mapping of symmetries, and that discovering 'good' mappings (for some criteria of 'good') is the practice of knowledge-making: the endeavour (though not uniquely) of science.

+++

$$
\vector{1}
$$

```{code-cell} ipython3

```

```{code-cell} ipython3

```
