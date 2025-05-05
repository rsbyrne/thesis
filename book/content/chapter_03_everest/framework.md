## Framework

We have discussed the problem and devised a philosophy to undergird a potential solution. We must now design that solution, starting with its outer surface, the public API. The framework we have devised is called *Everest*.

*Everest* is a kind of 'middleware' - that is, it sits between the objects that a user will interact with and the objects of the machine. It does not seek to export a user interface that is completely sufficient to every use case, nor does it purport to provide more efficient or capable algorithms for numerical computing itself. Instead, *Everest* should be thought of as a kit for building bespoke user applications that wrap around a field's customary numerical codes to dramatically improve their ease-of-use. Such applications are dubbed 'Engines' in *Everest*'s parlance: for example, "*PlanetEngine* is an application of *Everest* for planet-scale geodynamic modelling." The middleware assets provided by *Everest* are intended to be comprehensive enough that a user can build an effective, bespoke, and fully-featured toolchain for their scientific computing workflow without any specialist knowledge beyond a basic fluency in off-the-shelf *Python* code.

Written mostly in *Python*, a popular 'glue' language with broad utility and unrivalled extensibility, *Everest* provides a hierarchy of software objects that map to, and behave in the manner anticipated by, the *AKP* doctrine. While not unconcerned with machine efficiency - *Everest* is fastidious in exploiting *C*-level best practices wherever possible - our software is most concerned with *human* efficiency. It represents our direct attempt to resolve the Complexity Crunch by achieving a fundamental and permanent decoupling of computational complexity from logistical complexity. If a user of an *Everest*-derived application finds that it is as easy to run a one million-model survey as it is to run a ten-model survey, then the software has achieved its most important goal.

While an early version of *Everest*, *v0.1*, has been deployed at scale with great success since 2019, the current version, *v0.2*, continues to be developed alongside exciting new applications that exploit its powerful *AKP*-derived syntaxes. This thesis is itself an implementation and demonstration of the capabilities of the new *Everest*, with all text, numerical analysis, data management, and visualisation produced by or with the aid of *Everest* functions, objects, and interfaces.

In this short section, a general overview of *Everest* will be presented, focussing on its top-level syntax - the level that most users will interact with.

### The idea of *Everest*

*Everest* is a software application for creating, storing, manipulating, analysing, and communicating data. Borrowing patterns from its underlying doctrine, *AKP*, it offers a set of high-level structures that provide a concrete handle on such abstract notions as a project, a model, or a workflow, and a syntax that relates these structures to allow the succinct assertion of a scientific intention in a single line of code. Its ultimate goal is to minimise or eradicate all non-creative labour and so enable "science at the speed of thought".

At the core of *Everest* is the idea that there should be no distinction between a complete instruction set for an action and the product of that action. With *Everest*, the command that creates a dataset is the same as the command that retrieves that dataset from memory. Users are thus encouraged to think in terms of what they wish to observe, rather than in terms of how to produce those observations. *Everest* thus captures the most important feature of 'declarative' programming languages like *SQL*. At the same time, the twinned nature of *Everest* objects makes it easy to switch into a 'procedural' frame of mind to manually or semi-manually 'drive' models through the data production pipeline as the user sees fit. The same expressions that carry out very small actions of data production or analysis can be used to carry out vast actions across arbitrarily large and complex systems, guaranteeing that a workflow remains manageable by a human being no matter how large the project may grow.

### General structure and use pattern

Being a software tool, *Everest* reimagines the knowledge model expounded by *AKP* in terms of software and numerical data flows. At its highest level, it defines:
- The *Everest* 'Schema' - the basic unit of software reproducibility, containing all the code necessary to acquire and/or produce a certain kind of data.
- The *Everest* 'Case' - the provision of a 'Schema' under certain assumptions or with certain inputs, exposing an interface for retrieving data and providing a common repository for all model outputs.
- The *Everest* 'Concretion' - an active software application with controls for exploring, acquiring, and storing model 'configurations' (reproducible data packets).

In addition to providing a number of ready-made implementations of these structures for a variety of common data operations, *Everest* is designed from the ground up to encourage and facilitate the creation of user applications. This is primarily achieved by designing new model 'Schema', either be written from scratch with a little *Python* knowledge, or assembled quickly and intuitively from *Everest*'s growing library of generic patterns.

Models built from *Everest* kits are likely to be faster than typical user implementations, but may not be competitive with state-of-the-art implementations for a particular field. *Everest* supports the authoring of schemas whose primary function is to extend its own *API* over arbitrary code, allowing users to retain the production pipelines they understand and trust. On the output end, *Everest* stores its data in a transparent, sensitively annotated *HDF*-based format which is easy for unfamiliar users to interpret and manipulate. Exporting work to one's preferred maths and stats environments is easy.

With the choice or design of an appropriate schema, most of the traditional labour of a modeller is already done. An entire project team could work within a single schema for years, progressively exploring the potentially infinite 'space' of discoveries within it, sound in the knowledge that all the data produced along the way is being reproducibly and searchably stored without the need for any additional labour or logistical overhead. The advantages for productivity and collaboration are obvious.

### Top-level syntax

The *Everest* top-level syntax focusses on the idea of 'space' - searching it, slicing it, and naming it.

Consider a financial schema, `FinSchema`, that predicts how a market of a given composition will evolve over time from a given initial condition. A single 'world' (a 'Case') of this schema could be retrieved as follows:

```
>>> MyCase = FinSchema(companies1920s)
```

The new case `MyCase` could, for example, be a reconstruction of the major players in the American market during the 1920s. Let us now initialise this case at a particular point in history - Black Tuesday:

```
>>> mymodel = MyCase(blacktuesday1929)
```

This new object, `mymodel`, is a 'concretion' - a particular instance of its case - equipped with methods that allow the model to be 'driven' forward or backward in time, capturing data or producing visualisations along the way. Having initialised it with historical data for a particular day, let us now iterate the model by one day:

```
>>> mymodel.go(Days(1))
```

If our financial model is all we hope it to be, we would expect that the market at this point is not faring well.

If this was all that *Everest* supported, it would not justify the time and ink expended on it in this chapter. The real power of *Everest* is demonstrated at the higher level, by abstractly defining expanses of data across broad ranges of queries and assumptions:
```
>>> mydataset = FinSchema[
    [companies1920s, companies2000s],
    [blacktuesday1929, subprime2007] : [:Days(100)],
    ['dowjones', 'sap200'],
    ]
```
The result is a dataset containing eight 100-day timeseries: the Dow Jones and S&P200 indices for each of four scenarios, including the present market under 1920s conditions, and the 1920s market under 2000s conditions. Together, these datas could be used to test which of market composition or market valuation is more important in predicting a financial crash.

The goal of such a syntax is to align complex data operations with the way humans think and speak. In *Everest*, it should feel as easy to explain your intention to the machine as it is to explain it to yourself.
