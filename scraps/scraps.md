Technology has made research more complicated {cite}`Jay2020-nn`

Better software engineering practices needed, but also tailoring of practices to scientists {cite}`Heaton2015-wg`


- 'Deep' incisors are a kind of `tuple` (immutable ordered set) of other incisors, which can be a mix of trivial, broad, strict, and deep incisors. A deep incision applies each of its component incisors to the incised object in turn: first to the object's own content space, then to the content spaces of the objects represented by that space's points, and so on and so on. While a deep incisor could in a sense be viewed as a Space in itself, it is strongly typed as a *Python* tuple and does not participate in the Incision Protocol beyond its use as an incisor.




Each space is defined by one or more dimensions or 'Dims'. A Dim is a one-dimensional container with very permissive attributes. It need not be numerical, or even strongly typed. It may be continuous or discrete; its length may be finite, half-finite, infinite, or unknown; it may be open or closed. Its only strict requirement is that it is immutable. A *Python* `tuple` (immutable ordered finite set with arbitrary contents) is recognisable under the Incision Protocol as a special case of a Dim. The set of integers and the set of real numbers are also recognisable as Dims. Because a Space is defined as a set of Dims, and because a set under the Incision Protocol is itself a kind of Dim, Spaces are themselves Dims, and any Dim which contains at least one Dim is a Space. Spaces are thus free to 'contain' other Spaces. To distinguish between these contained spaces and 'subspaces', an unrelated concept, these shall be called 'bundle spaces'. The number of Dims a Space is equipped with is called its dimensionality or 'depth'.

An object equipped with such a space is said to be 'Incisable'. The Protocol defines an `Incisable` abstract class that formalises this quality, such that incisable objects always evaluate `True` when asked `isinstance(object, Incisable)`. (The `Incisable` class can also be subclassed directly, just like other *Python* container classes.) Being Incisable implies one and only one user-facing feature of an object: that it supports the square brackets notation, which should be conceived of as opening a 'window' to the Space 'inside' the object. To open up the 'content space' inside an object is to 'incise' that object: the product of that operation is called an 'Incision', and its argument is an 'Incisor'.

There are three kinds of incision, each achieved by passing one of three kinds of incisors into an incisable's content space:
- 'Trivial' incisors simply return the object being incised, or an identical copy of it: they are the equivalent of 'retrieving' every point in space, thus simply reconstituting that space under a new name.
- 'Broad' incisors return a version of the incised object (the 'parent') whose content space is a subspace of the parent's. The returned object is expected to be an instance of a subclass of the incised object and so be incisable in the same manner that their parent was incisable. As they belong to subclasses of the parent, broad incisions should be expected to be acceptable as an input anywhere their parent is accepted. A broad incisor will typically be a kind of Dim.
- 'Strict' incisors are vectors of the same length as the incised space's depth. A strict incision returns an object representing an individual 'point' in the parent object's interior space: the arbitrary contents which are conceptually 'contained' by that parent. If the parent is a class, the products of a strict incision should be instances of that class. If the parent is callable, the products of a strict incision should be of the same type as the return type of the call operation.

Because the dimensions of a given space can themselves be spaces ('inner spaces'), it is possible within the Incision Protocol to create objects of extremely high dimensionality that are nonetheless very compact.

## Top-level structure of *Everest*

In *AKP*, the underlying doctrine of *Everest*, there are three principal structures: the Schema, the Case, and the Concretion. At its highest level, *Everest* reproduces these three structures directly:
- A `Schema` is a metaclass.
- A `Case` is any class which is an instance of `Schema`.
- A `concretion` is any object which is an instance of a `Case`.

As in *AKP*, the `Schema` contains a space whose points include every legal instance - i.e. every `Case` - of that Schema. The dimensions of this space are the `Schema`'s Parameters. A particular `Case` can be accessed by calling the `Schema`, like any normal *Python* class:

```
Schema(**parameters) -> Case
```

