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

# The crisis of dimensionality

+++

How do you model an infinite frontier?

+++

In military science, there is a maxim: "Quantity has a quality all its own."

In the natural sciences, this maxim has a double-edged truth. Quantity - of observations, of experiments, of models - opens up new frontiers of discovery: not greater per se, but profoundly different to the frontiers of 'small-run' science. At the same time, quantity creates new technical challenges: again, not necessarily greater, but fundamentally different to the challenges of executing a narrowly-focussed study.

To the old maxim, we might add a corollary: "And different quantities may have different qualities too." In other words, not all forms of "big" science are created equally. The 2010s saw a boom in 'Big Data'. The promises made at that time were as sweeping and ecstatic as those attending today's AI boom. In many cases, however, the promised transformations were abortive, underwhelming, or simply not forthcoming.

Moving between scales successfully requires understanding what properties are preserved, lost, and changed in the scaling. It requires tools that are responsive to the unique qualities of working at a particular scale, and an appropriate mentality on the part of the scientist to recognise the costs and pursue the novel benefits on offer.

Geodynamics has always been at the vanguard of new methodologies, embracing numerical modelling, Big Data, and now AI, with energy and felicity. This thesis aims to contribute to that legacy by exploring the potential of highly object-oriented approaches to open up new ways to 'go big' on the model frontier.

At its simplest, this thesis is committed to exploring the potential benefits of a simple tradeoff between two kinds of 'quantity': lower resolution (quantity of calculations per model) in exchange for richer parameter space coverage (quantity of cases sampled). It will be shown how the journey from small-batch modelling to big-batch and, finally, truly massive suite-modelling, has entailed radically new approaches to designing, managing, shepherding, storing, organising, analysing, visualising, and even conceptualising big model runs for the big computing age - and not just for geodynamics, but for any field targeting similar 'shaped' problems.

+++

## Axes of complexity

+++

Most scientific modelling is focused on deeply exploring a tightly-chosen set of scenarios that relate to a real or hypothetical situation in some specific way. For that reason, it has traditionally sufficed to treat models as a kind of laboratory apparatus, even when the model itself is a numerical (software) entity that is not constrained in the ways that physical experiments are.

In this way of thinking, a model is a kind of machine, no different from a mass spectrometer or a centrifuge. Empirical data goes in one end, the machine is set to 'run', and model outputs pop out the other end. The analogy with conventional industrial processes is neither inapt nor accidental: the scientist features in this story as just another kind of technician on another kind of assembly line; the model is capital in the classical sense.

If we embrace this conception of 'model-as-machine' (and we will later show how this can be limiting and misleading), we can concentrate our analysis of scientific modelling on familiar economic grounds: labour, infrastructure, efficiency, productivity, and cost. Assuming that the engineers have done their job and that 'the machine' is as mechanically - or rather, computationally - efficient as it can be (also a limiting assumption), then productivity (output per unit of human labour) is the central metric of interest. The question becomes, simply, how do we make best use of the limited time of a skilled 'science technician' - that is to say, a scientist?

More crucially, how do we empower scientists and networks of scientists to take on more and better work with the same 'fixed stock' of resources? For we suggest that, just as industrial innovations have unlocked new scales of production - and thereby, new classes of product - so can innovations in the field of modelling expose new avenues of discovery.

As in manufacturing, the frontiers of scale stretch away from us on three (not entirely orthogonal) axes:

- Space: meaning actual physical space, but more acutely, factors of production that are embedded in space, like computational hardware, network infrastructure, and real estate.
- Time: meaning actual physical time, but more acutely, factors of production that are embedded in time, like CPU cycles, read-write time, labour time, and all sorts of *pro rata* costs, like electricity, water, depreciation, wages, and so on.
- Mass: the general 'systems complexity' of the model considered as a whole, including its human user; difficult to quantify, but related to codebase size, Big O analysis, Kolmogorov complexity, and Shannon entropy.

In the early twentieth century, a wave of 'Time and Motion' studies saw researchers dispatched to factories to document exactly how each action of each worker contributed to the final product. Let's set ourselves as a fly-on-the-wall of a typical worker in a modern 'science factory'. How does the labour of a modern modeller change as the task evolves across our three 'axes of complexity' - and where might better tooling make a decisive difference?

+++

## Space

What if the input data we are dealing with is not megabytes, or gigabytes, but rather terabytes - or even petabytes? What if the process demands not a handful of CPUs, but a warehouse-full?

The 'space' axis dictates what sort of machine we need to actually execute our model:

- Laptop science: fits comfortably on a good-quality laptop; a dozen gigabytes of RAM, less than a terabyte of storage, a dozen CPUs and/or a small GPU; thousands of dollars of hardware.
- Workstation science: fits on a powerful desktop machine; up to a hundred or so gigabytes of RAM, many terabytes of storage, dozens of CPUs and/or several top-shelf GPUs; tens of thousands of dollars of hardware.
- Node science: too big for any one physical machine, but still small enough that it can run on a single virtual machine, emulating a conventional operating system, but spread over multiple physical devices in a server cabinet; hundreds of gigabytes of RAM, dozens to hundreds of terabytes of storage, hundreds of CPUs and/or dozens of GPUs; hundreds of thousands of dollars of hardware.
- Server science: too big for a single stable VM, but small enough that it can run across a single tightly-connected physical network under a specialised operating system; petabytes of storage, terabytes or more of RAM, potentially thousands or hundreds of thousands of CPUs and GPUs; millions of dollars of hardware.
- Supercomputer science: too big for conventional computing altogether; exascale complexity footprints, hundreds of millions or billions of dollars of capital.

Note how each threshold introduces new infrastructure, new skills, new dependencies, and ultimately, new stakeholders to the project. Anyone can run any laptop model on any laptop, but it takes a skilled hobbyist to maintain a good-quality workstation and clever model design to exploit it. A node can be served by a generic VM provider *pro rata* without needing to involve anyone else in the project, but running a job on a whole server requires on-the-ground staff who are at least broadly aware of the needs and complexities of the model, not to mention highly specialised model architectures and the concomitant skills to drive them. Finally, supercomputer science demands tight coordination between user and provider and, typically, software that is specialised not just for supercomputers generally but for each supercomputer specifically.

+++

## Time

The 'time' axis introduces its own escalating ladder of difficulties:

- Trivial science: runs in the blink of an eye; e.g. drawing a scatter plot or averaging a spreadsheet.
- Hourglass science: takes long enough to run that the user becomes aware of it, but not so long that the user can background the process - e.g. loading a multi-gigabyte CSV file or rendering a 3D plot.
- Teabreak science: time-consuming enough that the user can safely background the process and gainfully focus on something else for a short time - e.g. running a clustering algorithm on a large dataset (while making a cup of tea).
- Redeye science: time-consuming enough that the user can safely change focus to an altogether different activity - e.g. running a mid-resolution fluid model (while flying overnight to a different country).
- Longhaul science: may take anywhere from a day to a week - e.g running a regional climate model while preparing a paper on the topic.
- Slowburn science: could take weeks, months, or even years - e.g. running a high-resolution galactic evolution model while writing up a paper on a totally different topic.

The escalating cost of compute with time is obviously one dimension of time complexity, but the labour cost also shifts in complex ways. At the 'trivial' level, there is no labour cost at all. At the 'hourglass' level, the user's time is mostly consumed (or rather, wasted) in tandem with compute time. From the 'tearoom' stage up, the user can make up time by switching tasks (though that incurs its own costs). At even longer time horizons, the assumption that human labour and machine labour run 'in parallel' starts to unravel. Long-running processes need shepherding: a mandatory update may trigger, or the power may go out, or some unforeseen resource limit may be stretched. The cost of mistakes and changes-of-mind also grows with time - potentially exponentially, if there are onward task dependencies; likewise the cost of bottlenecks, undershoots, and overshoots. At the higher end, the relationship of compute time and labour time inverts, as long-running projects demand increasingly vigilant stewardship.

+++

## Mass

The notion of model 'mass' is our attempt to unify in one noun a general sense of what makes, say, a Swiss watch more 'complex' than an Egyptian obelisk. Both are the product of an enormous amount of labour, but only one requires a substantial amount of maintenance. Our choice of the word 'mass' for this property is borrowed from physics, where the phenomenon of mass is ultimately related to symmetry breaking: that is, the more ways it 'matters' how a parcel of matter is oriented, the heavier it is.

Whereas the axes of space and time relate to what a model 'needs', model mass relates to what a model 'does', and how it does it. In keeping with the metaphor, aspects of a model that contribute to its mass are those that make it 'harder to move' (in that sense 'heavier'), disregarding all factors that can be remedied by provisioning additional 'space' or 'time' resources. We will move from the outside in, starting with the operator's perspective and moving down into the operational layer.

As we have discussed, every model has a boundary, and every boundary has an interface. The first and most obvious kind of model 'mass' is the complexity of its interface. The notion is intuitive for any tool, be it a software package or a spanner: the more capital it takes to operate the tool, the less 'portable' that tool is from situation to situation (it is in that sense 'harder to move'). This cost can be split into two parts - the 'take-up' cost and the 'in-use' cost. A system has a 'skill cliff' to operate has a high take-up cost; a system that demands full and persistent attention to operate has a high in-use cost.

The other kind of 'boundary mass' is lie in a system's dependencies: the sum of the connectivities a system demands in order to basically function. This is clearly demonstrated in the realm of software, where even a single dependency can invoke other dependencies, which invoke other dependencies. Chains - or rather, forests - of dependencies are hard to manage at the best of times. In the case of circular dependencies - where $A$ depends on $B$ but $B$ in some way precludes $A$ - it can be literally impossible to manage. Taken collectively, a system's dependencies can be viewed as a description of the kind of environment it expects to operate in. If two systems must coexist in the same environment and their dependencies contradict, one must be sacrificed: the mass of the first system has in a sense 'crushed' the second system.

These boundary costs are manifest regardless of whether the operator is a human, a computer, a non-computing machine, or even inert matter. For example, a hospital MRI machine demands extremely specialised infrastructure to support it, ranging from reinforced flooring and failsafe power systems through to specialised computer systems, neverending maintenance checks, and specially trained human operators. An MRI machine also expects to be integrated into the larger hospital system: data management, scheduling, rostering, all need to interface with the machine for it to fulfil its basic function. If the MRI machine deals in an unusual format or merely uses an uncommon screw type, the cost of managing that is born by the system in perpetuity. All these factors make an MRI machine not just literally heavy, but also 'massive' in the sense being developed here, because it is so costly to install, operate, and remove. When it finally becomes necessary for the hospital to replace it, these will all be strong arguments for getting a new one that is exactly the same.

As we move past the 'model boundary' (from operator concerns to operational concerns), we encounter various kinds of 'intrinsic mass': elements of model mass that arise from the permutations of the machine as it is operating.

A model can be enormously costly in space and time, and still be 'light' if it can be run with total ignorance about its internal workings. For example, modern Large Language Models are objectively gargantuan, but they are internally 'blobby' and are designed to be operated purely through their user-friendly chat interfaces. Part of what makes LLMs so 'light' is their internal statelessness, which dramatically reduces the cardinality of its permutation set.

Conversely, a model can be relatively trivial in space and time and still be tremendously 'heavy' if it requires comprehensive and vigilant monitoring. The ancient COBOL systems that run much of the world's banking infrastructure are systems of this kind, as are the signalling switchboards that many train networks still rely on. That these systems are 'massive' is proven by the fact that they have still not been replaced even decades after superior alternatives became available: they are simply too 'heavy' to move (or more precisely, the cost of moving them outweights the benefits).

A model's intrinsic mass is related to the extent to which it can be treated as a 'black box': in other words, how 'leaky' is its boundary? In our example of the MRI machine, we could have discussed the problem of its noisiness, or its vibrations, or its electromagnetic radiation. All of these attributes are necessary consequences of the proper functioning of the machine, but none of them are intentional. They have the consequence of limiting where the machine can go and what other systems can operate in its vicinity: in short, the 'purely internal affairs' of the machine exert a force on the environment that demands to be accommodated, as vociferously as its explicit dependencies do.

+++ {"jp-MarkdownHeadingCollapsed": true}

### The Problem, the Problem Problem, and the Complexity Crunch

It will not have escaped notice that several of the concerns we have covered under 'mass' remind us of elements of 'spacelike' and 'timelike' complexity, which we discussed earlier. This is because the three axes of complexity naturally and inevitably converge at the 'top'.

There is an obvious, physical sense in which this is so. Of course 'massive' models require space - where else are those internal permutations to be stored? Of course spatially extensive models are costly in time: even at the speed of light, we can only move information so fast. Of course time-consuming models develop more 'mass': more runtime means more opportunities for random errors to accumulate, which can only be managed by increasing model complexity.

However, there is also a lesss tangible force of convergence between these axes, that relates directly to the problem of 'complexity' itself.

Consider a problem, $P$ - which could be any problem, physical or digital. There are of course easy problems and hard problems: compacting the many dimensions of complexity, we can imagine casting all that 'problemness' onto a single axis.

We can choose to live with that problem, or we can choose to implement a solution, $S$. The solution is easy when the problem is easy, and gets more difficult as the problem gets more difficult. There are most likely wide swathes of problem space where the solution is almost equally easy even for different problem difficulties. Inevitably, however, there will come a point where the solution loses its 'grip' on the problem, and solution complexity skyrockets even for minor increments.

+++

## Model types

+++

### One-shot modelling

The simplest kind of modelling you could do is a 'one-shot' model. Performing a regression analysis on a collected dataset is one example: the inputs here are the data to be analysed; the outputs are the paremeters of the fit, including the error.

The 'workflow' is something like this:

1. Marshal the input data.
2. Configure the apparatus.
3. Feed in the input data and hit 'run'.
4. Wait.
5. Collect the outputs.

Preparing a one-shot model is easy. The data must be made available in the right environment and in the right format. Crucially, it can be stored under a completely arbitrary name - as can the output, and for that matter, the model itself. (We will later see how big an advantage this is.) If we want to guarantee reproducibility, we only need to tag the output with the input name and the model name. If we want to publish our work, we merely prepend our own name to the whole assemblage to make it universally disambiguous.

In terms of computer resources too, a one-shot is as convenient as can be. The input footprint is known. We may not exactly know what the runtime and output footprints will be, but we can usually guess. The amount of (machine) time required to run the model may not be known, but we can set up an alert to inform us when it is done, and in the meantime deploy our own labour gainfully in some other place. The labour-time running cost is therefore close to zero.

Without going out and doing a huge anthropological survey of all science, we cannot put specific numbers on how common this sort of workflow is: certainly, the number will vary between disciplines. For the field of geodynamics, we can say that it is very common indeed. We can see that a one-shot study has several virtues: it is easy to organise, easy to run, easy to comprehend, and easy to explain. The model itself may be complicated and costly - but up to a certain point, these are costs born by machines, not by humans. In a market where skilled labour is expensive and infrastructure is cheap (or, almost equivalently, in which labour is risky and infrastructure is safe), economic forces will militate in favour of the one-shot.

+++

### Chain-shot modelling

Given that the model apparatus in principle acts on generic data, there is nothing stopping us from feeding the outputs of one model into another model, and another, forming a 'model pipeline': the data equivalent of a physical assembly line. An unskilled operator might carry this out manually, paying a labour cost at each hand-off; a more skilled operator will recognise the redundancy and 'compose' these models into a single compound model, within which the component models are executed sequentially.

This could be called a 'chain-shot' model. The chain-shot model sits in a continuum with the one-shot model. If the cost and complexity of each 'handoff' is low, the whole model can be treated as a one-shot. When it can't, it must be analysed as a chain-shot.

Consider this example. Geoscientist Alice has a shapefile full of fault lines which she needs to map. Once she's mapped the faultlines (according to some 'model', tacit or otherwise), the faults are to be handed off to Bob for stress analysis (another model).

This is a chain-shot model with two 'links': Alice's part and Bob's part. Inbetween, there is some friction. The output format from Alice's side may not match the input format on Bob's side. Alice might have done her work on a laptop while Bob might have to push it onto an HPC cluster for his part. The data itself might be heavy or complicated.

Now say that helpful laboratory computer nerd Carol offers to help out by combining these two workflows into a more manageable 'one-shot'. Carol attentively interviews each worker and figures out what they need; then Carol writes a software module that sits in the middle, converting formats, organising data, and pushing it where it needs to go.

In principle, what Carol has actually done is create her own model, which is now wedged inbetween the other two. The degree to which Carol succeeds with her contribution determines whether the whole pipeline 'collapses' into a one-shot or 'inflates' into a three-shot. It is possible that Carol's model save the team hundreds of hours of labour and compute. It is also possible that Carol's model creates a new 'complexity point' which must now be managed in tandem with the others. (This is neglecting the cost of creating the 'third model' in the first place.)

In truth, even in the best-case scenario, there are always pros and cons to 'pipeline-ising' a workflow. The cost of automation is standardisation. For Carol's model to help more than it hinders, it needs to have a strong internal representation of what both Anne and Bob need. But Anne and Bob's needs may be variable or indeterminate. Once they are 'locked in' to Carol's model, it will be much more difficult to make adjustments or catch unpredictable bugs. (Imagine the pandemonium if Anne decided to change her output format one day!)

Carol can mitigate these problems by making her model more sophisticated, anticipating a wider range of input shapes and output requirements. Yet this, too, is a kind of inflation: it won't be long before Carol's zippy third model is the 'heaviest' and most complicated of the lot. We only need to look at how LLMs are used in modern data pipelines to see the endgame here.

Ultimately, whether a model counts as a one-shot or a chain-shot depends on whether the operator needs to pay attention to the model's internal boundaries. If the operator is able to be completely oblivious to the inner architecture of the model without impacting its stability or scope, we should consider it a one-shot. If not, it's a chain-shot - perhaps a relatively hands-off one, but a chain-shot nonetheless. A chain-shot will always be more 'massive' than a one-shot of the same computational complexity due to the additional overhead - however slight - of managing those boundaries.

+++

### Multi-shot modelling

The logical dual to a chain-shot model is a multi-shot model. Whereas a chain-shot model has tasks that must be executed in serial, a multi-shot model permits its tasks to be executed in parallel.

Here we will discuss the strict endmember where all models can be commenced at $t=0$ and the model as a whole is only deemed complete when every model in the set calls in. In a multi-shot, as in a one-shot, the operator has the luxury of stepping away from the action, freeing up resources for other tasks. Unlike a one-shot, however, the resource and complexity footprint of the model cannot be assumed to be uniform through space and time.

The principle pain-point of a multi-shot model is uneven complexity across its sub-problems. While all models - including one-shots - suffer from the 'scope problem', multi-shot models are exponentially more volatile. It is a simple matter of combinatorics: if each model can 'go wrong' (or 'be costly') in $n$ ways, then the set of possible scenarios across $m$ models is $m^n$. It may be that many of those scenarios are benign, but some may be diabolical.

Imagine Dan is running fifty CFD simulations, representing fifty different choices of a key parameter. The problem is posed such that the model results are useless until all fifty are in (otherwise it's not a multi-shot). Dan has a lot to consider when planning this campaign.

Dan might first wonder how long to wait before expecting any results. Typically, we have no way of knowing in advance how the choice of parameter will affect the difficulty of the resultant problem: there is every chance that Model A will resolve in minutes while Model E may take days. This has consequences both for Dan's personal planning and for his computer resource allocation. If Dan assumes that the runtimes will fall out on a bell curve, he can expect to waste something like half of his CPU-hours even in the case of modest variance. Dan's own time may be wasted in the same degree: either he waits to pounce on the results as soon as they're all in (a 100% waste of operator resources), or he determines to come back at regular intervals (preserving operator efficiency at the cost of system efficiency).

Dans' uncertainty

+++

##############################################################################

+++

Scraps

In the early twentieth century, a wave of 'Time and Motion' studies saw observers dispatched to factories to document exactly how each individual worker contributed to the whole. Let's set ourselves as a fly-on-the-wall of a typical scientific modeller.

(This economic force is demonstrated at scale in the modern AI sector, where each of the gigantic 'foundation models' (like GPT or Llama) is essentially the monolithic output of a single, multi-billion-dollar execution of a compound one-shot (the training pipeline) on a particular input set (the training data). That the output in this case is itself a model is an interesting detail we will pick up on later. The gargantuan size of these models creates 'a quality all its own' which .)

+++

## The LEGO problem

Viewed laterally, the challenge of building big models across a broad frontier is a kind of combinatorics problem. We call it 'the LEGO problem'.

Everyone is familiar with LEGO. Arguably the world's most successful toy, its ubiquity has led to a secondary legacy as a byword for modularity: such-and-such a thing is 'like LEGO' if it is made of discrete pieces that can be easily 'snapped together' in a fixed, but combinatorially explosive, variety of ways.

In short, LEGO is the quintessential example of a simplex-complex system.

LEGO's 'simplices' are the individual LEGO 'bricks'. Properly called 'elements' in LEGO's formal nomenclature (there is indeed a formal nomenclature), elements are manufactured individually, with each kind allocated a unique identity code. WHile originally there were only a few different kinds of LEGO element, today there are thousands, with every variant of the classic brick and plate types joined by a plethora of specialised types with dedicated technical and decorative functions: doors, windows, trees, hinges, gears, not to mention the 'minifigs' ('LEGO men') themselves.

Of course, what makes LEGO 'LEGO' is not its elements, but the patented connection system that allows them to be snapped together. There are actually a few different connection protocols in the LEGO system but the main one involves the 'studs' which dot the upper surface of most pieces, which are designed to snugly fit into the 'antistuds' (little holes) typically found on the base. Most LEGO elements offer multiple connection site - often a great many. Any two LEGO pieces locked together according to the system's legal connection rules are said to comprise a 'build'. Builds are thus the 'complices' of the LEGO system.

What qualifies LEGO as a true simplex-complex system is that the set of LEGO entities is closed under the operation of connecting: put simply, every LEGO 'build' can be treated as a LEGO 'element' from the point of view of the connection system. Two arbitrary builds offer as many possibilities for being 'snapped' together as two arbitrary elements do.

The purpose of the LEGO system is to afford its users (theoretically children) the pleasure of assembling whatever it is within them to imagine. Clearly, two collections of LEGO are not guaranteed to be equally utile *vis a vis* this objective. A LEGO set comprising a single grey brick (a 'degenerate' set in every sense) is not superior to one that includes a large number of pieces. Conversely, a set including many pieces, but only one kind of piece, is probably not preferred over a set with fewer pieces but greater variety. On the other hand, a set that includes every type of LEGO ever made, but only one instance of each kind, is probably not preferred over one that includes many generally useful pieces and a generous smattering of exotic ones.

The LEGO problem, phrased in terms of LEGO, is easily stated. Given the intuitive constraints on desirability, we ask:

*What is the ideal LEGO collection?*

There is of course no 'right solution' to this problem: but the form of the problem that makes solution possible will prove to have broad implications not just for the field of LEGO engineering but for simplex-complex systems generally.

### Formalising the LEGO problem

Drained of its colourful metaphor, the LEGO problem transforms into a subtle proposition with formal antecedents in combinatorics, abstract algebra, formal grammar, type theory, information science, and statistical mechanics.

We might say, for a given menu of simplices, $S$, and with respect to a desired set of target complices $C$, what is the set of enplices $E$ that optimisies the following partially-opposing criteria:

- **The frugality criterion**: we would wish for $E$ to be as small as possible.
- **The directness criterion**: we would wish for the recipes of $C$ to be as short as possible.
