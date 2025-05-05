# Implementation

We have discussed the motivations, underlying doctrine, and overarching framework of the *Everest* project. Now it must be shown how it actually works. In so doing, it will hopefully become clear just why the outermost user interface has the appearance it does, and why we have made the claims we have about the potential of this approach.

## Object-oriented programming

*Everest* is written in a heavily object-oriented paradigm. As not all will be familiar with OOP, a couple of terms will be defined here.

In *Python* and other languages, an 'object' is a persistent software asset with an address in memory that can hold data in the form of 'attributes' and run snippets of code called 'methods'. A program under OOP typically involves the creation, interrelation, activation, and destruction of an ecosystem of such objects to achieve the program's intention.

*Python* accesses objects by stating their name, which is assigned in an entirely context-dependent frame: one object can be known by many names in many places. Both attributes and methods are accessed using dot notation - for example, `myobject.foo` accesses the 'foo' property, which may be either an attribute or a method. Methods, once referenced, may be 'called' to execute their code with zero or more inputs using curved brackets - for example, `myobject.mymethod(myinput) -> output`. Objects may themselves be callable: for instance, `myobject(myinput) -> output`.

Some objects are designed principally to 'do' things, others principally to 'hold' things. For container-like objects, *Python* provides a square brackets notation (also called 'subscripting') which has the modal sense of retrieving something from somewhere - for example, `myobject[myslice]` returns certain datas from 'inside' `myobject` according to the criterion `myslice`. The *Pythonic* operation of 'slicing' into an object in this manner is related to the *AKP* notion of 'incision'; consequently, it will be seen that *Everest* syntax relies heavily on the square brackets notation.

Objects in *Python* and other languages always have a 'type', a kind of object to which they belong. An object's type can be viewed by asking `type(myobject)`. These types are called 'classes' and their names are usually capitalised - for example, `MyClass`. Every object has a type and is said to be an 'instance' of that type (what *AKP* calls a 'concretion'). Just as a labrador is a type of dog, which is a type of mammal, which is a type of animal, at the same time as being a type of pet, which is a type of domestic animal, which is a type of animal, classes in *Python* can subclass and superclass one another, forming branching 'inheritance trees' which provide properties and behaviours to objects whose classes participate in them.

Class inheritance may be tested by asking `issubclass(A, B)`, which returns `True` if `A` is identical to `B` or is a subclass of it. Objects may be tested for their membership by asking `isinstance(myobject, B)`, which returns `True` if the class that `myobject` is an instance of is either `B` or a subclass of it. Sometimes it is useful to define a class that behaves like an object's class without that object needing to be aware of it: *Python* supports these as 'abstract base classes' and they are frequently employed to define interfaces. It is a convention of OOP that instances of subclasses are accepted anywhere that instances of their superclasses are accepted, but not vice versa. For example, integers are real numbers, but the converse is not true; thus, functions which are valid for real numbers are valid for integers, but not the other way around.

Finally, in *Python*, classes are themselves objects, and so can own and do things without ever needing to be instantiated. Being objects, classes have their own type: the class that a class is an instance of is called its 'metaclass'. *Everest* pushes the *Pythonic* class machinery much further than typical *Python* applications do in order to more naturally map code objects to *AKP* constructs.

### *Everest* and OOP

The highly object-oriented nature of *Everest* is one major sense in which it deviates from previous approaches to large-scale computing. Whereas scientific computing traditionally has taken a procedural approach to computation, focussed on 'piping' data flows through shells on supercomputer clusters, *Everest* recognises that - for a work of scientific computing to be persistent - it must ultimately produce an 'object' of some kind. That object must be able to be stored in non-volatile memory - be that a hard drive or a reel of magnetic tape - and it must naturally offer a range of means of access so its import may be recognised in human minds where social knowledge is processed. Actions in *Everest* begin, rather than end, with the designation of objects, leaving the control flow behind those actions sufficiently muted as to almost reproduce a declarative (database-like) programming idiom. This is the soul of *Everest*.

## Generic *Everest* tools

Throughout this section, the names and functions of several generic *Everest* tools will be assumed knowledge. With no other natural context in which to introduce these, we will quickly go through some of them here.

### *Everest* utilities

Some tools are so generic as to defy placement even within the program itself. The only thing these top-level 'utilities' have in common is their lack of any dependencies beyond the *Python* standard libraries. In no particular order:
- `TypeMap` is a *Python* `Mapping` type with an unconventional `__getitem__` (square brackets) method based on comparing classes and subclasses. A 'typemap' is initialised with a mapping of types and items. Calling `mytypemap[x]` will iteratively compare the 'type' of `x` (or simply `x` if it is itself a type) to the keys of the provided mapping, stopping at the first key for which `issubclass(type(x), key)` evaluates `True`; that key is then used to retrieve the desired item. If no matches are found, the call may optionally be deferred to another typemap, or a default may be returned. Because both typemap instances and *Python* types themselves are immutable, the output can be cached so that future lookups are extremely quick. `TypeMap` is useful for imposing a kind 'strong typing' on procedures without completely sacrificing the intentionally dynamically-typed nature of *Python*.
- `FrozenMap` is an immutable *Python* `dict` equivalent. Being immutable, it can be hashed, and thus cached. *Python* lacks such a data structure natively.

### *Everest* Simpli

The `simpli` subpackage is the means by which *Everest* supports the *Message Passing Interface* (MPI) protocol for parallel computing. While MPI is certainly a very robust and versatile parallelisation method, it can be counter-intuitive to write for and tends to fail in opaque ways. The `simpli` package provides a number of context managers and wrappers that help the user write code that either runs smoothly in MPI or fails swiftly and meaningfully.

### *Everest* Reseed

The `reseed` subpackage is *Everest*'s solution for reproducible, thread-safe randomness. The `reseed` package defines the `Reseed` type. Initialised with an arbitrary chosen seed, each `Reseed` instance is a reproducible wrapper around a `NumPy` random number generator with some convenience methods to allow quick and easy retrieval of random numbers, sequences, text strings, and more.

To those who do not require the additional control that the `Reseed` class brings, access to its main methods is also facilitated through top-level independent functions which accept the choice of seed as a keyword argument. If no seed is provided, a single shared 'global reseeder' is used whose seed is established and fixed at startup. This satisfies the not-uncommon use case of a user or occasion that simply requires a random value or choice immediately and without fuss.

An extended functionality of `Reseed` exploits the *Python* `with` syntax to support reproducible and reversible 'blocks' of randomised computing:

```
>>> reseeder = Reseed(myseed)
>>> with reseeder:
...     print(reseeder.choice([1, 2, 3]))
2
```

At the termination of each `with` block, the state of `reseeder`'s random number generator is reset to what it was before the execution of that block, no matter how many randomised operations are carried out. This behaviour is guaranteed even in the case of multiple nested blocks: it is not necessary for any part of the program to be aware that it is being carried out within an already-open `Reseed` context.

The `reseed` package makes itself parallel-safe by means of its cousin, the `simpli` package. Paralle-safe randomness is critically important to code stability, indispensible for data reproducibility, easily overlooked by novice users, and - without the convenience of `reseed` - somewhat unwieldy to implement on a case-by-case basis. With `reseed`, random number generators established across multiple threads are always guaranteed to remain synchronised.

### *Everest* Classtools

To support *Everest*'s high-order object-oriented approach, it was necessary to develop new tools for class definition on top of those provided within *Python*. The `classtools` subpackage provides a number of 'adderclasses' that 'decorate' (wrap or add functionality to) native *Python* class definitions, allowing for many features including automatic addition of 'dunder' methods, reproducibility enforcement, and more.

An `AdderClass` is an abstract base class that can be used to decorate other classes, directly adding its own attributes and methods in order to transform the subject into an implicit inheritor of itself. Adder classes are useful because they allow the separation of the functionality-adding and 'quality'-altering natures of class inheritance, freeing up the true inheritance tree to more strictly reflect the latter over the former. They also lend themselves to metaprogramming (writing code that writes other code).

#### MRO classes

*Everest* provides and uses many adder classes, but the most important for this exegesis is the `MROClassable` class. This feature allows 'inner classes' (classes that are attributes, rather than instances or subclasses, of other classes) to be defined cooperatively across multiple layers of a class's inheritance tree - and even include the owning class as one of their bases.

In *Python* and other object-oriented languages, the various classes that form the bases of an object's type may offer different definitions for the same attributes, including methods. Rather than simply overwriting the parent bindings, objects and classes are provided access to those bindings in a separate namespace, enabling the subclasses to define functionalities that extend or augment the parent functionality. For classes with deep inheritance trees, the control flow of the program is successively passed up in a stable, linear succession called the Method Resolution Order or 'MRO'.

When a class (the 'added-to class') is processed by the `MROClassable` adder, the adder looks for certain class-defined special names and, for each name, loops through the MRO chain for any inner classes assigned to that name. These classes are then used as the bases of a new class, which is finally assigned to the added-to class under the original name. As an optional extra, the added-to class can itself be factored into the new 'MRO class' as either a base or a metaclass.

The 'MRO class' procedure has many uses throughout *Everest*. For just one example, the `Case` class is a 'metaclassable MRO class' of the schema it belongs to. This allows the schema to enforce a condition that all instances of itself are subclasses of its own special case class - and preserve this property even for its own subclasses. While there are other ways to achieve the same effect in *Python*, none are so compact.

## The Incision Protocol

*Everest* extends the traditional *Python* subscripting (square brackets) notation to make it both more flexible and more strict. The new notation is called the Incision Protocol, to differentiate it from conventional *Python* 'getting' and 'slicing' protocols. All public *Everest* objects which support subscripting do so according to this protocol. To those with some experience of *NumPy*, *Python*'s primary numerical computing package, the syntax will be familiar: it is effectively an extension of *NumPy* 'fancy indexing' with dimensions that may arbitrarily typed, irregular, infinite, or uncountable. Fundamentally, its intention is to generalise *Pythonic* 'getting' syntax to support the broader sense of an object containing having 'space'.

### Defining the chora

In mathematics, a space can be loosely defined as a set with some added structure. Beyond that, the concept of space is defined in many contrasting ways for many contrasting purposes. For clarity, let us instead appropriate the Greek equivalent, 'chora' (plural 'choraes'), and defines it as a set equipped with a mechanism for retrieving one or more elements. The Incision Protocol realises this definition with the `Chora` class, a type of immutable *Python* `set` with sockets that anticipate the imposition of structures by its subclasses. The `Chora` class is both the simplest type and the base type of all choraes recognised by the Incision Protocol; any instance of such is a chora, lowercase.

In its basic use case, the `Chora` class can be used just like a standard *Python* `set` by instantiating it with a collection of unique, arbitrary elements. `Chora`, however, has two crucial differences.

Firstly, instances `Chora` are not limited to contain finite sets. They can just as easily digest sets of unknown or even infinite length. The set of every possible combination of alphanumeric characters is a perfectly acceptable chora, as is the set of all real numbers. Many such useful sets are defined 'out of the box', most built on fast *C* level protocols that are much more powerful than typical user implementations. A consequence of being both unordered and potentially unlimited is that a basic `Chora` instance is not iterable, thus procedural access can only be carried out by random sampling without replacement.

Secondly, `Chora` instances support element retrieval by passing a request through the square brackets notation: `mychora[myquery] -> mycontent`. Under the Incision Protocol, subscripting operations on chora are called 'incisions', and any input to an incision is called an 'incisor'. There are three kinds of incisor:
- 'Trivial' incisors simply return the chora incised, or alternatively an identical copy of it; they are the equivalent of 'retrieving' every point in space, thus simply reconstituting that space under a new name.
- 'Broad' incisors return a view of the chora with added conditions and retrieval methods: in other words, they return a subspace of the incised space with new metrics attached.
- 'Strict' incisors return a single element from a chora, or - put another way - prescribe a vector singling out a particular point within the chora.

The basic `Chora` class supports three retrieval methods - one for each of the basic incisor types:
- Retrieval of its complete self by trivial incisor, returning itself.
- Retrieval of a single element from itself by equality comparison with a strict incisor.
- Iterative retrieval from itself by the same process across the elements of a broad incisor.

Beyond merely supporting its own intended functionality, the `Chora` class defines an architecture that supports the Incision Protocol in general. Upon invoking the `__getitem__` method (optionally via the subscripting notation `myobject[x]`), the following procedure is implemented:
1. The type of the incisor (the argument of `__getitem__`) is passed to the `get_incision_method` class method, where it is looked up in a 

### Chora subclasses

By itself, the `Chora` class does not offer much beyond the basic *Python* container behaviours. The power of chorae as a data structure is developed through its many subclasses. Here are a few of the most notable:
- The `Transform` class takes any other chora and applies a given unary function to every element.
- The `Ordered` class adds the sense of ordering of elements, and hence the notion of *Python* 'slicing', implemented here as a kind of broad incision across a given range; for example, `myordered[cond1:cond2:cond3]` would return the chora of all elements of `myordered` matching `cond3` after and including the first element satisfying `cond1` and up to but not including the first element satisfying `cond2`. A special subclass of `Ordered` is the `Reals` class, the set of all real numbers. While `Ordered` chora can be sliced, they still cannot be iterated nor indexed. These properties are added by subclasses:
  - The `Countable` class, which imposes countability on its elements, and thus supports iteration over its bounded subspaces, though not over itself. An ordered chora 'sliced' with a 'stride length' returns a countable chora. A special subclass of `Countable` is the `Integers` class, the set of all natural numbers.
  - The `Limited` class, which allows the assertion of either a 'highest' element or a 'lowest' element or both. An ordered chora 'sliced' with either a start or stop index returns a limited chora. A doubly-limited chora supports explicit and reproducible random sampling by slicing with a random seed. For example, `myreal[0:1:'aardvark']` returns an infinite, countable sequence of randomly selected real numbers between zero and one; any two such operations with the same random seed (e.g. the 'aardvark' string here) will return the same sequence.
  - The `Tractable` class, which subclasses both `Countable` and `Limited` and therefore supports full *Python* still count-based indexing - for example, `mytractable[2:5]` would return a `Tractable` traversing the three elements from position two to position four inclusive. An ordered chora sliced with a stride length and one or both of a start index and a stop index returns a tractable chora. The addition of both limits and countability permits iteration, making `Tractable` an implicit subclass of the native *Python* `Iterable` base class; however, only tractables with lower limits can be successfully iterated across.

The user is encouraged to define their own subclasses as they see fit.

### Chorae containing chorae

Many of the chora's most expressive uses derive from its ability to contain other chora. Several special subclasses are provided which explore and exploit the notion of a space 'containing' spaces:
- The `Metachora` class is a subclass of `Chora` that guarantees that all of its elements are themselves chorae. Its subclasses:
  - The `Cometric` class is a kind of `Tractable` `Metachora` whose contained chora represent equivalent metrics traversing the same space. At incision, the incisor type is compared to each metric's manifest of recognised types until a match is found. That metric is then incised, and the return value used to incise the next metric, and so on, until the last metric is incised and the final return value retrieved. The `Cometric` class is a generalisation of the idea of a mapping and can be used to create dictionaries with multiple key 'levels'. The fact that cometrics can contain other cometrics extends its use even further.
  - The `Multimetric` class is a kind of `Metachora` whose contained chora represent dimensions of a single multidimensional space (technically . A simple Cartesian plane would be implemented as a multimetric of two chorae of the `Reals` type. Incisions of a multimetric are delegated to its dimensions, returning a new multimetric whose dimensions are each reduced accordingly. This procedure is called a 'deep incision' and the incisor that carries it out is called a 'deep incisor'. Dimensions that are incised 'strictly' as a result of a deep incision are put in a 'collapsed' state and ignored in further deep incisions, effectively reducing the dimensionality of the whole space; 'broad' incisions, by contrast, preserve but reduce the dimensions they slice, defining a kind of subspace of the whole. The assignment of the element or elements of a deep incisor over the dimensions of the multimetric is itself a kind of incision, and it can be useful to define a cometric over the multimetric to manage this 'meta' incision; the dimensions might be orderd, for instance, or mapped to keys. Finally, multimetrics are of course free to contain other multimetrics. This allows the user to take a naturally n-dimensional problem and distribute those dimensions into 'deep spaces' according to some natural hierarchy. So important is this feature to *Everest* that supporting it alone motivated the entire design and implementation of the incision protocol.

### Advanced 


### The muddling algorithm

The chora is designed to support both assigning to and retrieving from potentially infinite spaces. This implies infinite iteration, which becomes problematic in the case of multiple parallel infinities: a Cartesian product over multiple infinite series will fail to advance beyond the first element of any but the first series. We can do better. The Incision Protocol proposes a 'mangling' algorithm which allows the even traversal of any tractable superseries of ordered, half-limited sequences:
1. First is yielded the set comprising the first element of each sequence.
2. Next is yielded the combination of the second element of the first sequence with the first element of every other sequence. This is followed by the combination of the second element of the second sequence with the first element of the other sequences, and so on.
3. Next is yield the combination of the third element of the first sequence with the first element of every other sequence, then the second element; this is repeated for each sequence, and so on.
4. The series continues as such forever. Sequences that become exhausted continue to provide their elements for future iterations but are not themselves advanced any further.
The intention of the mangling algorithm is to provide an intuitive way of digesting multiple infinite sequences by ensuring that all possible combinations of already-retrieved elements are fully explored before any new elements are introduced; in other words, at any given time during the mangling process, the quantity of elements retrieved from each sequence are guaranteed to be approximately equal.
