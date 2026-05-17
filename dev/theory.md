---
jupyter:
  jupytext:
    default_lexer: ipython3
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.19.0
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

```python
##############################################################################
```

# Theory


Before we proceed, we need to refine our conception of what a 'model' actually is.


## What is a model?

Like other terms of art that have emerged organically over time, the word 'model' is used in many different ways in many different places. In its original usage, the word referred to the sorts of miniatures that architects have traditionally built (and continue to build) to test the basic idea of a structure and, not unimportantly, to sell it to patrons.

Today, though there remains a place for physical 'models' (e.g. in aerodynamics), the term more often refers to a mathematical construct, and more often still, a computer program implementing a mathematical construct. Nevertheless, the central idea of creating a 'smaller version' of something to aid our understanding of the 'real thing' remains.

Working forward from that original definition, we propose the following formula. A model is:

1. A set of assumptions...
2. ...together with their consequences...
3. ...taken as a concise and sufficient representation of something else.

Statement 1 essentially describe a mathematical 'algebra' or 'calculus': the assumptions would be 'axioms', typically defining an inventory of operators and their relations. In formal linguistics, the same would usually be called a 'grammar': a system of rules that produce sentences from an 'alphabet' of generic symbols, or when reversed, 'parses' a flat sequence of symbols into a single hierarchicalised object. For our purposes, we adopt the general term 'Schema'. Every Schema is arbitrary in itself, irrespective of the motives of its architect: it is only necessary that a Schema be internally consistent ('sound'). Within that constraint, infinitely many Schemas can be devised.

On a deeper level, both the mathematical and linguistic ways of looking at a Schema transform into automata specifications: in other words, a sufficiently strict formalisation of a set of assumptions is necessarily a kind of computer program (the Curry-Howard Correspondence). The set of states reachable by the automaton is synonymous with the 'consequences' we allude to in Statement 2. There are many names for this abstract space where it arises in different contexts: in logic, the 'theory'; in set theory, the 'closure'; in linear algebra, the 'span'; in group theory, the 'orbit'; in formal grammar, the 'entailment'. We will simpy call it the 'domain', with both its space-like and mathematical implications.

Statements 1 and 2, taken together, describe a system amenable to study under pure logic. Though every Schema implies a specific domain, a given domain might be well-accounted for by many different Schema. A given Schema and its domain conceived as a single whole - a domain informed by a Schema, and a Schema expounded by a domain - forms a kind of object identifiable with the medieval concept of 'logos'. Mathematics, formal linguistics, and 'philosophy', considered broadly, could thus all be described as the study of logos (or rather, many 'logoses').

Finally we come to Statement 3. Thus far, we have established nothing that distinguishes us as modellers from the mathematicians, logicians, and grammarians. To leave the world of arbitrary axioms and inferential theorems, we must introduce the idea of 'representation': the object must be given a subject. This, at last, is what we would call a 'model': a logos interpreted as a representation of something else.

A model is as sound as the logos that drives it - and we would always hope that our models are sound, at least. However, the fact that a model is meant to represent something introduces new ways for it to be 'good' or 'bad'. The old modeller's adage has it that "all models are wrong, but some are useful". Statement 3 assesses the quality of the representation under two interlinked criteria which effectively recapitulate the wisdom of the adage:

- 'Concision' is of course a modeller's version of Occam's Razor, simply capturing the traditional scientific preference for parsimony. The justification for a criterion of concision is that the proper destination of knowledge is the human mind, which is always necessarily smaller than any real object of study. A model that is concise to the degree that its intended operator can wield it effectively could be said to be 'tractable'.
- 'Sufficiency' reflects the balance of what the modeller hopes to capture in the model, and what the modeller is prepared to sacrifice in exchange for it: in other words, how 'valid' is the model? Since nothing 'real' can be losslessly compressed, the criterion of concision implies a criterion of sufficiency, with the two usually traded off against each other according to the judgement of the modeller. Usually, the price of making a model more valid for one particular set of scenarios is to make it less valid as a representation of other scenarios - or indeed, completely invalid. Consequently it can be helpful to think in terms of a 'contingent validity' that defines a 'zone of validity'. Establishing this zone clearly is one of the essential tasks of a modeller.

The system of relationships between a logos and a chosen of subject - which gives rise to the 'model' proper - deserves its own term: this we might call the 'metaphor' of the model. The metaphor is the gateway through which information from the model flows out into the world, and vice versa. We can imagine a sort of 'metaphorical boundary' around model space. Empirical data is analogised to model data as it passes one way through this boundary, and model data is analogised to empirical data as it passes the other way. The model 'metaphor' empowers us to make declarative statements about reality from the standpoint of the model using the 'insofar' logical operator: "Insofar as $x$, $y$" - that is to say, "Insofar as Model X is valid, Model Inference Y is valid".

We started this exercise with a generally uncontroversial, plain-English definition of what a model is, then refined that notion with tighter specifications and new nomenclature. Translated accordingly, we can now in a position to declare more formally:

*A model is a representational logos that is sound, valid, and tractable.*


### The structure of a Schema


Though we have introduced the Schema as a mathematical or programmatic proposition, this is really putting the cart before the horse.

Kant ([@Kant1781-su]) introduces his 'Schema' as a sort of procedural rule, planted in the human imagination, through which sense data (the 'phenomenal world') is organised before we are even consciously aware of it. Without a structure of this kind, the world would be a soup of contentless, relationless sense impressions. What's more - as Kant radically observed - that structure *must* be prior, because it could hardly be acquired from the phenomenal world if phenomena themselves are not tractable until they are organised.

Today, Kant's idea is most commonly encountered in data science, where a 'Schema' is a system's 'recipe' for structuring outbound data and destructuring inbound data. A Schema is usually integrated into an interface, often an API ('Application Programming Interface'), that allows the outside world to control and be controlled by the system. The legacy of Kant remains visible in this conception of a 'Schema' because, again, the Schema is prior, and permanently conditions what the system can understand about the world - and what the world can understand about the system. The database cannot be built around the data: for the data to 'show up' at all, the database must already be there.

This conception of the 'Schema' as a kind of 'recipe for information' has a lot to offer as a methodological framework for empirical research. However, as faithful scientists, neither Kant's negativity nor the data scientist's utility are for us. We are interested in knowledge.

It is an odd quirk of the scientific profession that we are laser-focused on acquiring knowledge while simultaneously displaying a specific and at times aggressive disinterested in knowing what 'knowledge' actually is. This is not a luxury that the modeller can afford. For while a botanist who discovers a new orchid is readily recognisable as a 'scientist doing science', the same cannot be said for a modeller running models unless the outputs can be swiftly reconnected to reality. It is as if the stopwatch starts as soon as we cross the 'metaphorical boundary', and if we don't return with the goods in short order, we are abandoned there. This attitude forecloses the possibility that there might be real knowledge to be gained from a long sojourn through model space. The botanist who disappears into the jungle for ten years is hailed as a scientific legend: the modeller who spends as long inside a model is lambasted as a crank.

The value of Kant's observation is to remind us that we are in fact *always in the model domain*. No matter what kind of science we're doing, there is always a Schema, there is always a metaphor, and there is always a model. The only difference between modellers and other kinds of scientists is that the modeller wields the arbitrariness of the model deliberately, as a tool.


### Information systems and knowledge systems


To design an instrument and to use it effectively, we must have a clear notion of what it is meant to do. So let us be crystal clear: a model is an instrument for producing knowledge. Like other things that humans do instinctively, like chewing, knowledge-making is "easier done than said". But if we want to develop the art of modelling, we must make the implicit explicit, however obnoxious that seems.

So - what is knowledge?

We would say:

*Knowledge is an internal symmetry that corresponds to an external symmetry.*

And thus we can say:

*Knowledge-making is the mapping of external symmetries to internal symmetries.*

Traditionally, the 'external symmetries' would be observables in the physical world, and the 'internal symmetries' would be neural firing patterns within the human brain. However, the relaxed framing of our definition allows us to conceive of other kinds of knowledge. In principle, our definition implies that knowledge-making is possible anywhere we have:

1. A pair of systems
2. A boundary between them
3. An 'agentic disparity' between the two sides - i.e. the actors have greater control over one side than the other side.

These three statements define what you could generally call an "information system". The 'low agency' side is the 'outside'; the 'exterior'; the 'environment'. The 'high agency' side is the 'inside', which could be any kind of mutable 'stuff'; we will call this the 'epistemic substrate'. The 'boundary' between them the two sides - the 'epistemic membrane' - admits signals (in both directions, though for now we are principally interested in the inbound traffic): these signals are what we call 'information', in the literal sense that they have the potential to 'inform' the interior about the state of the exterior.

Information systems are all around us, and most are not very intelligent. A robot vacuum cleaner is a classic example of an information system, and anyone who owns one will attest to how easily flummoxed they are. However, an information system's ability to absorb information and to use it to mutate its own state endows it with the potential to become something greater: a knowledge system.

A knowledge system is an information system where the primary mode of response to new information is to reconfigure the substrate so as to maximally correlate with that information. The product of that correlation is knowledge, defined as above, and the process is knowledge-making. While information systems are common, knowledge systems are rare; the province of complex life, and not all complex life at that.

The knowledge system we are most intimately familiar with is the human mind. For an individual human, the membrane is the 'wall of the self': the 'outside' is the real world and the 'inside' is the imagination. Through attention and repetition, we can capture features ('symmetries') of that outside world and 'store' them internally as memory engrams. The difference between idle daydreams and what we esteem as 'knowledge' is exactly that, and only that, the 'thing inside' correlates to that 'thing outside'. We instinctively recognise that there is value in such a mapping, and science in its ancestral form is just this, done deliberately.

Science, of course, is today a much larger endeavour. It is a social project - that is to say, a purposeful society. A society is another kind of information system. The 'outside' is now the non-human world together with the part of the human world that is not 'kin'. The 'inside' is the society itself. The 'substrate' is the collective memory surface of all the individuals making up the society, together with all non-human information technologies (books, computers, specimens in jars, et cetera). The 'membrane', in the case of our scientific society, is a densely instrumentalised frontier of experimental apparatuses and observational devices - not to neglect our own natural observational faculties, which are far from obsolete. The society of science - 'the Academy' - acquires information through this membrane (sometimes passively, often actively) and processes it into sophisticated internal representations that attempt to recapitulate important features of the outside world. Those representations - whether physical, like books and papers and graphs, or purely extant in the minds of the society's members - are the 'knowledge' that make science at large a coherent 'knowledge system'.


### Schematising information into data


We have described the endpoints of knowledge creation, but we have glossed over the crucial step: how exactly does a knowledge system act on inbound information to produce knowledge?

We must return now to our schemes and logoses, our models and domains: for these are the instruments that make it possible.

We have been careful to use the word 'information' thus far, instead of the word 'data'. That is because information only becomes data when it is structured by a Schema. An information system equipped with a Schema becomes what we could call a 'data system': a halfway-house between an information system and a true knowledge system. Data, in a sense, is the 'sacralised' internal messaging language of a data system: its 'autonomous protocol'; that is, its contract with itself. Data is a refined artifact, laden with the system's own conventions and convictions, produced for the benefit of internal processes only, and incomprehensible to the outside world.

Kant's observation of the priority of the Schema now returns to haunt us. For if it is given that the 'system' is smaller than its environment, it will never be possible for the system to anticipate all the information that might arrive. In adopting a Schema, an information system acquires powerful new affordances, but at the cost of making part (perhaps virtually all) of the larger world incomprehensible: and again, as per Kant, the decision about what to include and what to exclude - what 'counts' and what is uncountable - must be made 'on spec' - or perhaps 'on faith'.

Tight Schemas produce efficient data. Storing, processing, and messaging are all accelerated as a Schema is made more intolerant. When it becomes necessary for one data system to communicate to another, this can be accommodated without undue complication by establishing a 'protocol': a contract between two Schemas that allows data to be converted from one Schema to another, possibly through several intermediaries. Extremely prescriptive Schemas are essentially what we call 'formats', and many protocols are simply directives for all participants to convert their data into a common format before communicating. (JSON is the quintessential example of this.)

It is tempting to view data as the end of the epistemological pipeline. However, while data is without doubt a more useful product than information, data does not by itself contain anything that the root information does not. A network of thermometers could be set up as a data system, and its product - a table of finite-precision values in a chosen unit sampled over discrete time intervals - would without a doubt be more useful than the raw temperature information bombarding those sensors; but this is just an arbitrary filtration of information, transformed into data by means of its arbitrariness. Knowledge is more.


### Open and closed Schemata

It will shortly prove helpful to distinguish between two broad types of Schema: 'open' Schemas and 'closed' Schemas.

An open Schema expects to receive totally arbitrary information and is prepared to ignore much or all of it when converting phenomena into data. A closed Schema has much stricter requirements: it expects to receive only information that can be structured into data according to local rules.

The Schemas that Kant discussed we might describe as 'open': the information of our senses, which rushes unbidden into the imagination and is immediately, transparently, and frictonlessly structured as mental impressions that the mind knows how to act on; all that does not fit is discarded.

Language, by contrast, would be an example of a 'closed' Schema: there is legal and illegal English, and a person attempting to address another person in gobbledegook may be asked to repeat themselves. This example is specifically chosen because it is precisely the option of appeal that allows languages to be closed in this manner: we cannot appeal to the universe when our senses of sight or hearing confuse us - nor, for that matter, can a camera or a microphone.

We should always expect to find that the outermost layer of any complex of data systems is built on an 'open Schema': without it, no system can communicate with the world, whether to understand it or to act upon it.


### Schemas as spaces

Earlier, we presented the notion of a 'Schema' as a productive, self-consistent set of rules for manipulating symbols. The set of all configurations that can be interpreted, or equivalently, produced by a Schema, we termed the 'domain'.

Implicit in our characterisation, but not explicitly stated, is that there is nothing that necessarily binds a domain to a particular Schema. Just as the same computer file can be 'read' in many formats (not just the one its original author 'intended'), the same domain can be apprehended by infinitely many conceivable Schemas.

To understand this, it can be helpful to take our choice of words literally and view a 'domain' as a kind of space, with the Schema as a kind of ordering over that space - more precisely, a topology. The infinitesimal 'points in space' of the domain correspond to what are variously called 'primitives', 'elements', 'symbols', 'terminals', or (due to AI) 'tokens'. Honouring the spatial metaphor we are developing, we will call them 'points'. These are the atomic, indestructible, unique, prior-existent units of discourse that a given formal system knows how to manipulate.

When viewed this way, it becomes clearer why a Schema is naturally a specification for an automaton. We can picture a little robot - a robotic turtle, if that aids the imagination - dropped at a particular 'spot' in the domain and trundling off according to the logic given by its Schema. As it travels, the automaton reveals the topology of the domain under its given Schema.

It is because different Schemas can share the same domain - wholly or in part - that data systems are able to enter into a 'protocol' for inter-system communication. To send data from one to the other, we simply program the turtle to trundle off to some place in the overlap zone that encodes the information we want to share. As soon as the turtle arrives, the originating Schema relinquishes control and the receiving Schema assumes control. From there, the turtle trundles off deep into the receiving Schema's domain, bound for territories potentially far beyond the comprehension of the original Schema.

We now have a way for Schemas to communicate, but how does an 'open' Schema communicate with the universe? Can this be viewed in a spacelike way? For an open Schema, phenomenological information arrives 'from elsewhere': it is extra-Schematic; trans-cosmic; truly outer. For this reason, an open Schema is best thought of as a domain whose territory can be stimulated spontaneously. This is literally true, for example, in the human eye, where the retina - with its finite and discrete assemblage of rod and cone cells - represents a tangible two-dimensional surface that is spontaneously and perpetually stimulated by incoming light from the actual, real world. The retina is an 'open data system' (a data system built on an open Schema) whose domain overlaps with the domain of the occipital lobe - a 'closed data system'. Incident light, in a sense, 'spawns' automata (optical signals) on the retina that travel into the overlap zone, get handed off to the lobe, and travel under its power into the richly structured terrains of its domain, far beyond the conception of the retina.


### The problem of compounds


We have conceived of the domain as being an inherently unstructured bag of arbitrary 'points', with each point itself having no substructure. This aids our 'spacelike' conception but leaves it unclear at first how higher structures are to be derived. Without higher structures - that is, 'compounds' - we are stuck in 'flatland' with no means to pursue useful abstractions.

There are several ways to deal with this limitation. One would be to emulate the Turing Machine and endow the automaton (our 'turtle') with a memory. With the Roman alphabet as our 'domain', the word 'pot' (a compound of 'p', 'o', and 't' in that order) could simply be represented as the turtle's memory of having previously 'visited' those locations in that order.

This classic solution, however, concedes far too much. Granting the turtle an 'inside' leads us to an infinite regress: it's almost as if there is a 'domain' inside the turtle, and voyaging through that domain, little turtles, and so on: turtles all the way down. In any case, it turns out that such an approach actually sacrifices parsimony needlessly: the turtle's memory, and even the program that governs its movements, can always be projected onto the symbol space itself, and the turtle navigated to equivalent endpoints under a generic, stateless program. This is hardly an improvement though, as the 'space' through which the turtle moves is now so cluttered with procedural information that the actual 'meaning' gets lost.

An alternate approach would be to admit the existence of 'compounds' as first-order citizens of our ontology. This is the approach taken in formal grammar, where 'non-terminal' symbols are introduced that represent combinations of 'terminal' symbols and other non-terminals. This approach, however, also has its drawbacks. Philosophically, it is objectionable in that it 'multiplies kinds' in violation of Occam's Razor. The ontological status of these ghostly 'non-terminal' symbols is unclear - are they 'real' or are they contrivances? Worse, these constructs have a tendency to 'consume' the semantically meaningful tokens at the bottom of the hierarchy, making whole classes of relationships untractable.

Modern (non-formal) linguistics is closer to the mark, postulating the existence of a neuroscientifically meaningful cognitive operation dubbed $\mathrm{MERGE}$. As in formal grammar, $\mathrm{MERGE}$ operator acts on groups of syntactic objects to produce higher objects: the difference is that $\mathrm{MERGE}$ acts on (unordered) sets instead of sequences and does not consume (or even subsume) its constituents, which may participate in multiple 'merged' objects simultaneously. A classic example is:

$$
\mathrm{MERGE} \{ \mathrm{female}, \space \mathrm{sovereign} \} = \mathrm{queen}
$$

This framework for conceptual abstraction, owed to neurolinguistics, today underpins Large Language Models like GPT, in which higher concepts are represented as superpositions of vectors representing simpler concepts. This powers a sort of 'conceptual algebra':

$$
\mathrm{king} - \mathrm{male} + \mathrm{female} = \mathrm{queen}
$$

This sort of space-like thinking is close to the framework we wish to expound here, albeit with many important differences.


### Sub-Schemas and sub-spaces


The route we are going to go down now borrows even more explicitly from the realm of geometry and linear algebra, driving us deep into the 'spacelike' mental model we are labouring to cultivate.

First, consider the set of real numbers, $\mathbb{R}$. The Cartesian product of $\mathbb{R}$ with itself, $\mathbb{R}^2$, gives us the Cartesian plane; $\mathbb{R}^3$ extends us into the third dimension.

If we treat $\mathbb{R}$ as a domain (with the real numbers as its 'points'), then $\mathbb{R}^3$ is clearly a structure of points - a kind of 'compound', which is what we were looking for. Yet we are also perfectly comfortable viewing $\mathbb{R}^3$ as a space in itself, whose 'points' have every bit the same ontological status (the same 'realness') as the 'points' of the number line $\mathbb{R}$.

Cartesian space is a simple example, but we can construct much more complex ones if we wish. There is nothing stopping us, for instance, from defining a three-dimensional space where one axis is drawn from the integers, one from the naturals, and the other from the reals. If we like, we can even 'bundle' our dimensions. Picture a tennis ball: it can both be situated in space ($\mathbb{R}^3$) and oriented in space (another $\mathbb{R}^3$ if we go with Euler, or $\mathbb{R}^4$ if we use quaternions). Effectively, the point representing each tennis ball 'contains' a whole multidimensional space of its own. Add in the colour of the tennis ball and you have another $\mathbb{R}^3$ at least. A given tennis ball at a particular point in space, oriented a particular way, and bearing a particular colour, can thus be thought of either as coordinate in a nine- or ten-dimensional space, or as space that can be reached via another space. Our freedom to dimensionalise the problem as we wish already suffices to generate all the structures we could want.

We can borrow this behaviour for own system by allowing 'layered Schemas'. The bottom layer contains the most degenerate tokens: those for which no substructure exists and in which no substructure will be sought. This layer could contain, for example, the Roman alphabet. The next layer contains points which each correspond to a group of points in the underlying layer. This layer could contain, for example, all legal English words. Over that, one could place a layer whose points correspond to groups of words (i.e. phrases or sentences). A 'turtle' programmed to navigate this top layer can access the information at the next layer down by dispatching a 'sub-turtle' to that layer; that sub-turtle can access the bottom layer by dispatching its own 'sub-turtle'; and so on.


## The Pleroma


It will be recalled that domains are meant to be independent of Schemas. If the Schemas are layered, that would seem to imply that their domains are layered; that however would be an inappropriate contamination of the domains' concerns by the Schemas' concerns. In principle, domains must be allowed to be independent of each other and of the Schemas that topologise them. Paradoxically, the most parsimonious way to support this independence is to unify all domains with each other.

We have shown how complex objects (compounds) can be represented as vectors of simpler objects, where each dimension represents some 'basic' notion and points off-axis represent 'higher' notions. This effectively represents syntactic objects as coordinates or vectors - that is, as groups of scalar multiples of primitive objects. We have the choice to formalise these groups as ordered (tuples), or as unordered (sets). Since concepts are not naturally (or at least, not self-evidently) orderable, and in keeping with the convention from neurolinguistics, it seems we must choose the latter. Furthermore, since the dimensions across which concepts are only identifiable by the relationships between the concepts that they embed, it seems that the dimensions themselves are interchangeable, i.e. not only are they without inherent order, but they are without inherent identity.

The mathematical structure that satisfies all of our requirements is somewhat exotic.

Here we introduce the notion of the 'Pleroma'. Formally we state:

*The Pleroma is the symmetric product of a countable infinity of open symmetric hyperreal unit intervals.*

Informally, or rather, metaphorically, the Pleroma serves as a sort of 'omni-domain' in which all specific domains are merely regions.

Let's step back for a moment and build up the intuition behind this idea.


### Symmetric axes


Now, it might occur to us to represent each concept as being somewhere in the range $0$ to $1$, where $1$ suggests "completely $x$" and $0$ suggests "not at all $x$". However, there is a third state to consider: "neither $x$ nor not $x$". This may seem esoteric, but the distinction is natural and vital. Consider the tape on a Turing Machine, or equivalently, the memory buffers inside a modern computer. We are comfortable with decomposing data into a binary form - $1$ and $0$, or in a more generic nomenclature, 'flip' and 'flop'. Now, there is a world of difference between a slot in a memory buffer that is in 'flop' ($0$) state and a slot that is in fact presently unallocated. This suggests a third state: 'empty'. If we wish to admit degrees of 'on-ness' and 'off-ness', with one extreme allocated to one end of the unit interval and the other allocated to the opposite end, then we have nowhere to store this 'third state' without creating some special 'option' type that admits 'empty' as a valid state.

A more elegant solution is to adopt the range $-1$ to $1$ (the 'symmetric unit interval'), and thus allow values approaching $0$ to bear the missing connotation of 'empty' - or, more precisely, 'irrelevant'. This has the added virtue of bringing about a quantitative equivalence between the sense of $x$ and not $x$, which logically are co-equal in strength as declarative claims. The king-queen equation from before is also simplified:

$$
\sum \space \mathrm{king}, \space \mathrm{antimale}, \space \mathrm{female} = \mathrm{queen}
$$

Effectively, we can do away with addition and subtraction altogether and have only scalar multiplication and the $\mathrm{MERGE}$ operation, which acts on sets:

$$
\mathrm{MERGE} \{ \mathrm{king}, \space \mathrm{antimale}, \space \mathrm{female} \} = \mathrm{queen}
$$

Such small parsimonies turn out to matter a great deal when building a complex formal system.


### Open hyperreal intervals


So far we have been assuming a closed interval (i.e. $1$ and $-1$ are acceptable values). However, permitting fixed endpoints of this kind inadvertently creates two 'kinds' of value: the extremes (with neighbours only in one direction) and the rest of the values (with neighbours in both directions). This requires any operators acting on the interval to be aware of the endmember cases, which introduces an artificiality to the formalisation. What's more, philosophically, if values on this scale are meant to represent 'degrees of confidence', we the existence of endmembers forces us to dignify the existence of 'absolute certainty', which seems unreasonable.

We could adopt instead an open interval, in which the endmembers may be approached but not reached. This, however, brings its own issues: situations where it is practical to admit 'arbitrary confidence' must settle on an arbitrary value close to the extremes, and the choice of that value will always tend to imply more than is intended (why $0.99$ and not $0.999$?)

There is a way we can have our cake and eat it too: we can take the values 'infinitesimally close to' $-1$ and $1$ and treat them as first-class objects rather than abstract limits. This produces what is called the 'hyperreal' number system, in which every real number is effectively surrounded by a 'halo' of infinitely many values, all infinitely close to the real value.


#### Hyperreals: a quick primer

The hyperreal number system is defined using the $\mathrm{st}$ operator, which returns the 'standard part' of any number, i.e. the number shorn of its infinetesimals (so in a sense 'rounded' to the nearest real value). One of the powerful consequences of hyperreality is that it gives us infinitely many 'ways to be a number', because for each real number there are infinitely many hyperreals whose 'standard part' is equal to that number:

$$
x \ne y
\\
\mathrm{st}(x) = \mathrm{st}(y)
$$

When it is necessary to explicitly refer to the part of the number that is 'left over' when the standard part is removed - the 'non-standard part', if you will - we often use $\epsilon$ (epsilon) for 'empty' (or in this case, empty for all practical purposes but not *actually* empty). A number $\epsilon$ is any number whose absolute value is closer to zero than any positive real number, but which is not itself equal to zero: in this sense it can be viewed as a shorthand for any variable drawn from the set of all infinitesimal values $\mathbb{I}$. In most other ways, $\epsilon$ behaves like a normal real: so, for example, $2 + \epsilon$ denotes a hyperreal number infinitesimally close to $2$.

The community of values that are all infinitesimally close to each other - because they are infinitesimally close to the same real number - was termed by Leibniz the 'monad'. We can define a monad function that retrieves this community for any given real:

$$\mathrm{monad}(x) = \{ x + \epsilon : \epsilon \in \mathbb{I} \}, \space x \in \mathbb{R}$$

It will shortly prove necessary to speak of numbers that reside in monads generally (i.e. the set of all hyperreals that are not real); we can extend Leibniz's Gnostic nomenclature and dub these 'monadics'.

One way of looking at the monad is that it 'thickens up' every real, turning it from an infinitesimal point with 'no content' to a space of its own with potentially rich internal structure. We shall term this the 'inherent space' of the number: a space which can be put to many uses.

Just as all non-zero reals have an inverse (e.g. $2$ has $1/2$), every number $\epsilon$ has an inverse, denoted $\omega$ (omega). Similar to $\epsilon$, a number $\omega$ is any number who absolute value is greater than any positive real number - a so-called 'transfinite' number. Multiplying a given $\epsilon$ by its associated $\omega$ returns the real value $1$, just as you get when multiplying any other number by its reciprocal. Multiplying an arbitary $\epsilon$ by an arbitrary $\omega$, however, produces an 'indeterminate' quantity whose value depends to the relative rates at which the pair grows and diminishes.

Numbers in the hyperreal system which are neither infinitesimal ($\epsilon$) nor transfinite ($\omega$) - i.e. which are 'close' to a standard real number other than zero - are termed 'appreciable'.

When using 'epsilon-omega' notation, as we shall from time to time, it will be important to always keep in mind that $\epsilon \neq \epsilon$ and $\omega \neq \omega$ - because by the definition of the hyperreals, there are infinitely many ways to be infinitesimally close to something, and a single symbol cannot represent each of those ways uniquely.

<!-- #region jp-MarkdownHeadingCollapsed=true -->
#### Hyperreal intervals

An open hyperreal interval between $-1$ and $1$ by definition contains all the real values between those two endpoints *as well as* all hyperreal values infinitesimally greater than $-1$ or infinitesimally lesser than $1$. Effectively, we have values in our system that are 'equal to' the endpoints from the point of view of the reals, but infinitesimally distant from them from the point of view of the hyperreals:

$$
x \ne y \ne -1
\\
\mathrm{st}(x) = \mathrm{st}(y) = -1
$$

The upper lower infinitesimals provide us with perfectly adequate proxies for 'flip' and 'flop' (thing and anti-thing) without breaking any maths that expects a uniformity of kinds or the freedom to always 'go a little bit further'.

Because there are infinitely many 'ways to be a number', hyperreality effectively provides two different ways for things to be 'the same'. We can say that numbers are 'equivalent' ($\approx$) if they have the same standard part and are 'identical' ($=$) if they share the same infinitesimal part too. This maps neatly to the concept in object-oriented programming (e.g. Python) where 'objects' are distinct from 'values', and where two things may be 'equivalent' (in Python, `x == y`) if they, as it were, 'evince' the same value, but are only 'identical' if they are literally bound to the same address in computer memory. So it is with hyperreal numbers, where 'object-ness' is likewise produced by a value's 'address', and we can freely have two $1$s that 'mean the same' (they have the same standard part) but are not the same (they are 'physically' in different places). This property will shortly prove very useful.

There is one final trick we can perform here. In the same way that we were able to 'pare away' the endmembers from the hyperreal interval without making them 'unreachable' as reals, so can we 'rake out' all the rest of the reals without losing the ability to do real arithmetic. Effectively, we are replacing the real number line with an infinite sequence of monads, and turning the 'standard part' operator into a sort of statistical instrument that returns the centroid of each monad 'as a real'.

This 'raking' unavoidably leaves holes in the number line - but if the 'reals' are constructed as the centroids of monads, then the holes are in the non-standard part, not in the standard part. Consequently, if a value is dragged from one point in the real number line to another (e.g. from $0.2$ to $0.3$), that value continues to move smoothly from the perspective of the reals, even if it 'actually' has to 'skip' over the centroids from the perspective of the hyperreals. So long as we preserve the ability for variables to range freely over 'all' the reals, we can handle th

What's left after the 'raking' is just the 'monadics', as we termed them earlier; as a set, we might call them the 'semi-hyperreals' - that is, the hyperreals without the reals. There is a proper way to do this that preserves higher mathematics, but that is surplus to requirements for now. What's important is that we are now free to assign different functions and meanings to reals as opposed to monadics.

How we interpret this new distinction is a matter of discretion, but the most natural interpretation is to view the reals (the monad centroids) as representing 'kinds of things' and the monadics as representing the 'actual things'. Alternatively, if we think of the hyperreals as a providing a kind of 'inherent space' inside each real point - as we discussed earlier - then the distinction between reals and monadics could be something like the distinction between a computer directory (a 'folder') and the files within that folder (the 'documents'). We will later show how these two seemingly different framings are actually fundamentally alike, and both relate to the properties of hyperreals in useful ways.
<!-- #endregion -->

#### Monads and micro-monads

We 'created' the hyperreals by postulating the existence of numbers ('monadics') that are closer to a given real number than any other real number is. The cloud of monadics associated with each real number we called its 'monad', and every real has one all to itself.

It might occur to us that the same technique could be used on the monadics themselves.

Take a real value, $a$. Somewhere in the monad of $a$ lies an arbitrary monadic, $b$. This number $b$ is surrounded by other 'co-monadics', all belonging to the same monad - the monad of $a$.

Now, restricting our view to just the monadics, can we imagine some infinitesimal value, $c$, which is closer to $b$ than any other monadic of $a$? Certainly we can: and the set of all such points forms, essentially, a 'micro-monad' around every monadic under $a$.

These 'micro-monadics' are normal monadics from the point of view of the reals, but from the point of view of any given real's monadics, they are monads unto themselves. The analysis can be applied recursively, with micro-micro monads and micro-micro-monads. All are 'indigenous' (that is, they are 'first-class citizens of') the hyperreals; but depending on one's point of view, they can be seen to possess rich internal structure, forming a hierarchy of monads inside monads inside monads.

While this analysis does not create any 'new' numbers - all are normal citizens of the hyperreals - it does add new structure, effectively endowing every hyperreal number with an 'address' that specifies which number it is 'closest to' at each level. This is the hyperreal equivalent of 'rounding to the nearest $n$', except that there is an infinite amount of 'space' within each layer.


#### Plenty of room at the bottom

So far we have strictly remained in the hyperreals. However, there is nothing stopping us from taking the whole technique of hyperreal construction and applying it to the hyperreals themselves to produce 'hyper-hyper-reals'.

While the micro-monads were constructed by restricting the realm of comparison to one 'layer' at a time, the hyper-hyper-reals appear when we stipulate the existence of numbers that are closer to any particular hyper-real than *any other hyperreal*; and whereas our analysis of micro-monads only provided new context for numbers that 'already existed' in the hyperreal system, our 'hyper-hyper-reals' include new numbers slotted into a new - and 'larger' - number-line.

If we denote the reals $\mathbb{R}$, and the hyperreals ${}^*\mathbb{R}$, we can define the 'hyper-hyper-reals' as ${}^{**}\mathbb{R}$, and the 'hyper-hyper-reals' as ${}^{***}\mathbb{R}$. If we do this ad infinitum, we produce a kind of 'ultimate' number system, dubbed the 'surreals' (symbolised '$\mathrm{No}$' for 'Number').

The surreals were named by Donald Knuth in his commentary on John Conway, who developed the notion during his study of boardgames. In Conway, as here, the hierarchy of infinities produces a kind of serial addressing system. In the same way that every number on the real number line can be seen to host a 'halo' of infinitesimally proximal values around it in ${}^*\mathbb{R}$, moving down to ${}^{**}\mathbb{R}$ reveals that each of *those* values in turn hosts its own 'halo' of values, and so on, and so on.

Surreality effectively endows every value with its own infinitely wide, infinitely deep 'file tree'. What's more, this extra storage capacity is in a sense 'portable' with its host value, since the standard part of any hyperreal number can be freely altered without impacting its non-standard part. Since at present we are only using the 'top layer' of this hierarchy (the hyperreals), all the layers from ${}^{**}\mathbb{R}$ down are free to use.

Between micro-monads and hyper-hyperreals, it is apparent that the 'inherent space' in each real number is not only infinitely capacious, but powerfully and deeply structured. This will become very useful down the track.


### Infinite dimensions


The final thing we need to consider is the number of dimensions we are prepared to admit. Large Language Models can have millions of dimensions; the popular BERT model uses vectors $768$-dimensional space to represent a corpus vocabulary of $\gt 30,000$ tokens. If we instead take our dimensions to represent, say, flip-flop states in a supercomputer, we could easily be talking about billions or trillions of dimensions. If we are driving towards universality, it is clear that there is no particular number, and no safe maximum number, that provides representational space for all kinds of data systems. What's more, intuitively, it feels axiomatic that there is no limit to the number of 'concepts' in the universe.

It stands to reason therefore that the space we are contemplating has infinitely many dimensions, and what's more, that these dimensions are uniform and unordered (the technical term is 'indiscernible'). More subtle still, these dimensions are without prior meaning and are therefore interchangeable: a symmetric product, rather than a Cartesian product.

It is this infinity of interchangeable, orthogonal axes that gives us the true Pleroma.

The most famous example of an infinite-dimensional structure in conventional mathematics is the Hilbert Cube, which is the ordered Cartesian product of an infinite sequence of real-valued intervals where, for each dimension numbered $n$ from $1$ to infinity, the lower bound is $0$ and the upper bound is $1/n$. Having the dimensions become progressively 'smaller' was Hilbert's way of ensuring that distances are finite even between points that are remote from each other in infinitely many ways. It transpires that the same can be accomplished by simply defining distance in a way that takes the value of $n$ into account, then simply prescribing the same $0$ to $1$ interval on each one, making the Hilbert Cube simply an infinite cousin to the conventional hypercube.

Even granting this simplification, the structure we are imagining here is somewhat distinct from the Hilbert cube:

| Property | Hilbert cube | Pleroma |
| ------------ | ------------ | ------------ |
| Cardinality | Countable | Countable |
| Ordering | Well-ordered | Indiscernible |
| Identity | Unique | Interchangeable |
| Uniform | No | Yes |
| Type | Real | Hyperreal |
| Interval | Closed | Open |
| Bounds | $0$ to $1$ | $-1$ to $1$ |

Note that, for both the Pleroma and the Hilbert Cube, we are dealing in two kinds of 'infinity' simultaneously. Within each dimension, there is an uncountably infinite number of degrees of feedom ('the cardinality of reals'). Across dimensions, however, we only support a countably infinite number of degrees ('the cardinality of naturals'). Of course, infinity is still infinity, and the fact that the number of dimensions is infinite means the Pleroma, like the Hilbert Cube, can be subdivided into infinitely many infinite-dimensional subspaces. In other words, the Pleroma contains itself, infinitely many times - so there's plenty of space in there.

With infinitely many dimensions, each point effectively becomes a countably infinite set of hyperreal values - one for each dimension. In the same way a single hyperreal value can be forced to the 'nearest' real using the $\mathrm{st}$ operator, we can define a 'standard form' operator $\mathrm{sf}$ that collects the set of standard parts of every coordinate at once. This effectively 'sends' the Pleroma to the Hilbert Cube, except with a symmetric interval and without the inherent ordering of dimensions. We can in a sense visualise the Pleroma as being 'really' this simpler, standard-valued space, but with an infinitesimally wide 'cloud' of infinitely many points surrounding each 'real' point.

Recall as well that our Pleroma is a symmetric product, not a Cartesian product. What this means is that each point is neither a 'tuple' (a sequence of values, like a vector) nor a 'struct' (a collection of labelled values). Instead, just as the axes are themselves unordered and interchangeable, so are the elements in each point. Therefore our points are properly represented as *multisets of hyperreal values in the symmetric unit interval*, where a 'multiset' is an unordered collection with duplicates permitted. The Pleroma itself can then be thought of as the *set of all countably infinite multisets whose elements are drawn from the open symmetric hyperreal unit interval*.


### Special points


It can be seen that a single hyperreal open symmetric unit interval contains exactly four 'special points':

| Name | Condition | Boolean |
| --- | --- | --- |
| Flip | $\mathrm{st}(x) = 1$ | True |
| Flop | $\mathrm{st}(x) = -1$ | False |
| Null | $\mathrm{st}(x) = 0 ,\space x \ne 0$ | Neither true nor false |
| Void | $x = 0$ | Inactive |

When extended into infinite, unordered dimensions, we have infinitely many ways for things to be 'true' or 'false' - but we still have certain special points. Taking an infinite-dimensional point $X$ varying across infinite dimensions $D$, we have:

| Name | Condition | Boolean |
| --- | --- | --- |
| All-flip | $X$ is flip for all $D$ | True |
| All-flop | $X$ is flop for all $D$ | False |
| All-null | $X$ is null for all $D$ | Neither true nor false |
| All-void | $X$ is void for all $D$ | Inactive |

All-flip and all-flop are conceptually the 'top' and 'bottom' corners of the Pleroma. All-null and all-void are two different ways of looking at the origin.

In distinguishing between 'false', 'neither true nor false', and 'inactive', we have a basic toolkit for data systems in the Pleroma. For example, let's take our test point, $X$. The point rests at all-void to begin with. If we move it infinitesimally in two chosen dimensions, without moving it in the other infinitely many dimensions, we have essentially 'selected' the standard 2D Cartesian plane. We can freely move our point around that plane without troubling ourselves with the other dimensions: we can even move the point through the origin, and - so long as we remain infinitesimally distant from 'actual zero' - we will never risk 'colliding' with any particle moving in any of the 'inactive' dimensions.

Now, say we 'activate' eight dimensions instead of just two. Our test point rests at null across those eight dimensions, but even though there is no 'signal' yet, the 'space' where that signal will go is prepared. This is analogous to reserving computer memory for an eight-bit integer: the 'flip' and 'flop' states on each axis become the ones and zeros. If we set aside three of these 'eight-spaces', we have the address space for an RGB colour value: and again, we can freely configure any of those three eight-spaces without inadvertently entering any of its peers, because the hyperreal interval gives us ways to 'be at zero' that only our 'home dimensions' can recognise. Even if we move our test point right 'through' the origin, the hyperreals allows us to do this smoothly 'in the reals' without actually impinging on true zero - unless we choose to.

Finally, if it becomes necessary for some reason to move our test particle $X$ from dimensions $(a, b, c)$ to dimensions $(b, c, d)$, we can do that by simply 'dropping it' to actual zero ('void') in dimension $a$ while simultaneously 'lifting it' infinitesimally above actual zero ('null') in dimension $b$. Thus we have the means not only to partition space into non-overlapping sub-spaces, but also to instantly 'tunnel' any particle from one such partition to another; and since the sub-spaces themselves are merely artifacts of the positioning of the points within them, we can also create, destroy, resize, and reshape sub-spaces at our leisure simply by moving a single point.

These sorts of 'tricks', enabled by hyperdimensionality and hyperrealism, will eventually allow us to build sophisticated programmable data systems. Before we can do that, however, we need to bring the Pleroma down to earth.


## Polytesimals

We can bring a little order to things by restricting our analysis to only those hyperreals that can be represented as the result of a power series on a standard infinitesimal - we'll use $\epsilon$ from before:

$$
x = a \epsilon ^ {0} + b \epsilon ^ {1} + c \epsilon ^ {2} ...
$$

The first term is the 'real' part. The second term is the 'first monadic layer'; the third term is the 'second monadic layer', and so on. For numbers of this form, the 'standard part' function is effectively just a function that discards all terms higher than power zero - we could imagine a 'second degree standard part' that discards only the terms higher than power one, and so on; thus it can be seen how $\mathrm{st}$ really is a 'rounding' operator.

Considering only the non-standard part of $x$ - that is, all the items in the power series from the first power up - we have a kind of 'infinite infinitesimal polynomial'. This attractive structure deserves an attractive name: the 'polytesimal'. Formally, we can define the polytesimals $P$ thusly:

$$
\begin{align}
P(\epsilon) = \sum_{k=0}^{\infty} a_k \epsilon^{k+1} &= a_0\epsilon + a_1\epsilon^2 + \dots
\\
&= \epsilon \left( a_0 + a_1 \epsilon + \dots \right)
\end{align}
\\
\mathrm{st}(P) = 0
$$

Where $\epsilon$ is an arbitrary infinitesimal and the coefficients are exclusively real numbers.

In principle, a polytesimal can be interpreted as a sequence of ever smaller 'steps'. We start at zero. The first 'step' takes us $a_0 \epsilon$ away from that position; the second 'step' takes us $a_1 \epsilon^2$ away from *that* position; the third 'step' takes us $a_2 \epsilon^3$ further again; and so-on. With each step, we effectively move into another 'nested' monad, because no real multiple of $\epsilon^n$ will ever be 'precise' enough to reach a coordinate given in $\epsilon^{n+1}$ (we will always either 'overshoot' or 'undershoot').

As for $\epsilon$ itself - the 'infinitesimal base' - this could be any value, and the choice is important: two polytesimals with different bases might as well be in different universes, since no choice of coefficients on one polytesimal will ever have the exact right degree of 'fineness' to reach the value of the other polytesimal.

We might say that the choice of base situates the polytesimal in a certain 'genre', and conversely, that a genre of polytesimals can be defined simply by choosing a base, which could be any infinitesimal - even another polytesimal. Two polytesimals are 'compatible' so long as they share the same genre. We could say that two polytesimals sharing the same genre are 'cogeneric'. We will presently demonstrate that every polytesimal belongs to one genre and to exactly one genre, and that observing the uniqueness of genre is equivalent to observing that there is only ever one valid infinitesimal base for any polytesimal.

Notationally, we will represent the 'genre of polytesimals based on $\alpha$' as $\mathbb{J}_\alpha$ - from the 'j' sound of 'genre'. (The meaning of $\mathbb{J}$ without the subscript will be discussed later.)

Since a polytesimal is fully characterised by its infinitesimal base and its coefficients, we can use the genre symbol to introduce a more concise notation for polytesimals:

$$
\mathbb{J}_\alpha \begin{bmatrix} a & b & c \end{bmatrix} = a\epsilon + b\epsilon^2 + c\epsilon^3
$$

With the addition of this matrix-based notation, it should hopefully make sense why we defined the infinite sum for polytesimals starting from index zero: it ensures that the coefficients are subscripted with their (zero-based) matrix coordinates.

Infinitesimals drawn from $\mathbb{J}_\alpha$ are 'very close to' (in the same monad as) $\alpha$. In fact, every genre technically includes its own base as a member, since $\alpha$ is equivalent to the polytesimal $(1\cdot\alpha + 0\cdot\alpha^1 + \dots)$).


### Special polytesimals and the nil polytesimal

In any given genre $J = \mathbb{J}_\alpha$, we can identify two 'special' polytesimals characterised by unique sequences of coefficients:

- The **trivial polytesimal** $J[1]$ is equal to its own genre's base ($\alpha$).
- The **identity polytesimal** $J\begin{bmatrix} 1 & 1 & 1 & \dots\end{bmatrix}$ is the sum of the infinite series of powers of the base where all the coefficients are unit.

We might ask what would happen if we took $J[0]$. The result would of course equal zero. Being zero deprives the number of the sole qualifying property of polytesimals established so far, which is that they can be uniquely identified with a certain genre. If $J[0]$ were allowed to qualify as a polytesimal, it would necessarily be a member of every genre simultaneously, violating this precept. If on the other hand we were to reject $J[0]$'s candidacy as a member of $J$, it would no longer be possible for $J$ to 'cover' the reals, which would destroy their most useful property.

We need to carve out an exception to handle this special case. The most non-destructive way to do this is to introduce a special infinitesimal value, 'nil' - symbolised $\pmb{\underline{\circ}}$. We will construct nil explicitly at a later point, but for now let us simply state that it is given to be vastly smaller than, and incompatible with, any other 'arbitrary' infinitesimal we might introduce and any infinitesimal that can be constructed thereof.

Now we declare an exception to the rule about polytesimal coefficients: each coefficient must be either:

1. A real value,
2. A real multiple of a positive integer power of $\pmb{\underline{\circ}}$ (a *quasinull* $\mathbb{R}^{\pmb{\underline{\circ}}}$),
3. The sum of a real value and a quasinull (a *quasireal* $\mathbb{R}^{+\pmb{\underline{\circ}}}$), or
4. A real multiple of a quasireal (necessarily also a quasireal).

Note that (real) $0$ is technically a 'quasinull', as we have here defined it.

Carving out this special case allows us to include terms in our polytesimals that resolve to zero in a real sense but retain genre information when viewed in a hyperreal sense. It also empowers us to define a third 'special' polytesimal, based on nil:

- The **nil polytesimal** $J[\pmb{\underline{\circ}}]$ is equal to $\pmb{\underline{\circ}} \alpha$ and thus functions zero for real arithmetic.

Because nil is defined as vanishingly small - even for an infinitesimal - it functions as zero from a real perspective.

- Adding nil to a polytesimal $p$ produces a (non-polytesimal) hyperreal infinitely close to $p$.
- Multiplying a polytesimal $p$ by nil produces a new polytesimal $q$ whose coefficients are all infinitely close to zero.
- Dividing by nil is not strictly undefined, like dividing by zero, but it is 'explosive', producing an enormously transfinite number that is guaranteed to dominate any subsequent arithmetic.

Adding or multiplying by the nil polytesimal is subtly different:

- Adding the nil polytesimal to a polytesimal of base $\epsilon$ introduces a new $\epsilon^1$ term, if none existed; if there is already a term $a\epsilon$, it is modified into $(a + \pmb{\underline{\circ}})\epsilon$ (i.e. the coefficient becomes quasinull).
- Multiplying by the nil polytesimal converts every coefficient into a quasinull, thus 'sending them to zero' from a real standpoint. A side-effect, however, is that the power of every term is incremented by one.
- Dividing by the nil polytesimal is explosive in a similar manner to dividing by nil.


### The formal definition of a polytesimal

It is easy to recognise a polytesimal when we ourselves have constructed it. It is less obvious how we recognise a polytesimal found 'in the wild', since it is not essentially of a different 'kind' than any other hyperreal number.

What makes a polytesimal a polytesimal is its infinitesimal base. In principle, as we have just shown, it is always possible to 'draw out' at least a single power of the base as a common factor because by definition the base is a factor of every term. We can develop that intuition to provide a more rigorous definition of what a polytesimal's base is and how it can be extracted:

*A number is a polytesimal if there exists a non-quasinull infinitesimal - its 'base' - which divides the polytesimal such that the result deviates from a real number by an increment that is either a quasinull or a polytesimal of the same base.*

This definition will have to be revised a couple of times before the end of our discourse on polytesimals, but let us esteem it true for now.

The definition implies that the process of identifying a polytesimal is the same as the process of extracting its base, and further, that base extraction is a recursive procedure. For a given candidate value $x \not\in \mathbb{R}^{\pmb{\underline{\circ}}}$ and a given 'trial infinitesimal' $\epsilon \not\in \mathbb{R}^{\pmb{\underline{\circ}}}$ :

1. Divide $x$ by $\epsilon$ and subtract the standard part.
2. If the residue is a quasinull then $x \in \mathbb{J}_\epsilon$; halt.
3. (Else) let $x$ be the residue and repeat.

Note that this algorithm does not return 'true' or 'false' but simply 'halts' (implying true) or runs forever.

The fact that the algorithm runs indefinitely in false cases makes it impractical for many purposes. We might decide instead to permit a provisional solution where we declare $x$ to be a member of $\mathbb{J}_\alpha$ 'up to' a certain power of $\alpha$. If we do this, we can reconstruct the polytesimal in its standard form using the same algorithm above just by keeping track of the number of iterations $k$ (starting from zero) and taking the discarded standard part as the coefficient of each added term $\alpha^{k+1}$. In this way, any hyperreal number that is not a quasinull can be at least approximated as a polytesimal up to a given power. We could call this *polytesimalisation*; so:

$$
\mathrm{poly}_\alpha^m \left( p \right) = \sum_{k=0}^{m-1} a_k \alpha^{k+1}
$$

Where each $a_k$ is the real value discarded from the $k$th iteration of $\mathrm{poly}$.


### What's in a genre?

Earlier we declared rather blithely that polytesimals of one genre can never 'overlap' with those of a different genre - i.e. that they exist within remote monads. We can demonstrate this is so by considering what is actually 'in' a genre - i.e. how 'big' and how 'small' can its elements get?

Because polytesimals are sequences of powers of infinitesimals, the lower-powered terms are actually larger than the higher-powered terms. Since the powers must be within the natural numbers greater than zero, the lowest power - and therefore the largest possible term - of a polytesimal in $\mathbb{J}_\epsilon$ is $\epsilon$ itself. When such a term is present, all the other terms are rounding errors - indeedly, infinitely smaller than rounding errors - by comparison.

The only way we can make the zeroth term 'larger' is by adding more $\epsilon$ to $\epsilon$ - that is, by increasing the magnitude of the (real) coefficient. The reals, of course, increase without bound, but it is an axiom of the hyperreal number system that its infinitesimals are always smaller - and its transfinites therefore always larger - than any real number. Thus no (real) value of $a$ can cause $a\epsilon$ to be any more than infinitesimally far from zero, no matter how 'far' we get away from $\epsilon$.

If we want to drive in the opposite direction, we can construct arbitrarily small polytesimals in $\mathbb{J}_\epsilon$ by taking higher powers of $\epsilon$ and smaller coefficients. The power increases with the natural numbers - unboundedly, yes, but nevertheless never to magnitudes comparable to $1/\epsilon$. We can actually get smaller faster by adjusting the coefficient: we can set it to be a quasinull. Since these are based on powers of $\pmb{\underline{\circ}}$ - already given to be incomparably smaller than any other infinitesimal in the scope of this discussion - any term with a quasinull coefficient is going to be smaller than any non-quasinull term no matter how large its power is. (This is intuitive if we think of quasinulls as 'zero-like' since, in the real numbers, $0$ is similarly 'always less' than any number no matter how small raised to any power no matter how big.)

Exactly 'how small' we can get with nil terms can be shown by taking the expression ${\left(\pmb{\underline{\circ}}\epsilon\right)}^n$ and steadily increasing the value of $n$ through the naturals. Even after a single increment of $n$, we must concede that the coefficient is already so small as to make the 'infinitesimal base' virtually infinite by comparison. Once a nil value is in play, nothing else really matters.

In the hyperreals, as in the reals, it is meaningless to speak of a 'largest' or of a 'smallest' item in any open set. Nevertheless, for the sake of our intuition, we can at least resort to the observation that the members of $\mathbb{J}_\epsilon$ are in the vicinity of epsilon at most, and somewhere within an infinite power of nil from zero at least.


### Properties of polytesimals

Polytesimals are both similar to, and profoundly different from, standard polynomials.

Like polynomials, the sum, difference, and product of polytesimals are all themselves polytesimals. Also like polynomials, polytesimals, as we just saw, can be 'substituted in' for each other and still remain polytesimal. Polytesimals can also be factored, which will become useful down the track.

An important difference is in the matter of equality. Polytesimals, like polynomials, ultimately resolve to a single value somewhere on the number line. However, unlike standard polynomials, every unique polytesimal resolves to a unique value: that is, two (cogeneric) polytesimals are only equal if all of their coefficients are equal. This is because no real coefficient of $\epsilon^n$ is small enough to reproduce the effect of adding even the largest possible value denominated in $\epsilon^{n+1}$ - the latter will always be 'finer' by a factor of $\epsilon$.

A related difference is in the matter of ordering. Because each subsequent power of the infinitesimal base is infinitely smaller than the preceding power ($\epsilon^n \gg \epsilon^{n+1}$), polytesimals exhibit 'lexicographical ordering', also known as 'dictionary ordering': any set of polytesimals can be ordered by their first coefficient, then their second coefficient, and so on.

Like any infinitesimal, a polytesimal can be added to any real number to produce a hyperreal: the real number is the 'standard part' and the polytesimal is the 'non-standard part'. To distinguish the two parts, for the sake of analysis, we'll adhere to the convention that the standard part is notated with lowercase Roman letters and the non-standard part - the polytesimal - by lowercase Greek letters:

$$
\alpha = \epsilon \left( 2 + 3\epsilon + 5\epsilon^2 \right)
\\
A = a + \alpha = a + \epsilon \left( 2 + 3\epsilon + 5\epsilon^2 \right)
$$

If we instead try to multiply a real number by a polytesimal, we simply get a polytesimal: if we want to preserve the standard part through this operation, we need to add $1$ to the polytesimal first. Borrowing notation from linear algebra, we'll denote these 'unit polytesimals' with a 'hat':

$$
\hat{\alpha} = 1 + \alpha
\\
A = a\hat{\alpha} = a + a \alpha = a + 2a\epsilon + 3a\epsilon^2 + 5a\epsilon^3
$$

<!-- #region jp-MarkdownHeadingCollapsed=true -->
### The Zoom operator

We are already familiar with idea of taking the 'standard part' of an infinitesimal number. The rigid structure of polytesimals allows us to be extend the notion of 'taking the standard part' into something a little finer.

Strictly speaking, the standard part of any polytesimal is zero, since - as defined - polytesimals have no $\epsilon^0$ term. We can however 'lift' a polytesimal 'closer to reality' by dividing by its genre's base and discarding any newly non-infinitesimal terms (since it is now, conceptually, 'too close to see').

We call this the $\mathrm{zoom}$ operation:

$$
\mathrm{zoom}(a\epsilon^1 + b\epsilon^2 + c\epsilon^3 + ...)
= b\epsilon^1 + c\epsilon^2 + ...
$$

For example, say we wanted to 'zoom in' on the polytesimal $a\epsilon^1 + b\epsilon^2$:

$$
\begin{aligned}
\mathrm{zoom}(a\epsilon^1 + b\epsilon^2)
&= \frac{a\epsilon^1 + b\epsilon^2}{\epsilon} - a
\\
&= b\epsilon
\end{aligned}
$$

Of course, this operator must 'know' the value of $\epsilon$ in order to function. When this value isn't obvious from context, we will allow it to be provided explicitly as a subscript: e.g. $\mathrm{zoom}_\epsilon$ would be read as 'zoom with respect to $\epsilon$'.

We can imagine an infinite hierarchy of recursively applied $\mathrm{zoom}$ operators:

$$
\mathrm{zoom}^1, \ \mathrm{zoom}^2, \ ..., \ \mathrm{zoom}^\infty
$$

When a polytesimal's terms are ordered by increasing power (including the zero terms), applying $\mathrm{zoom}^n$ has the effect of discarding all terms up to $n$. If we then subtract the result of an even deeper zoom, we can 'select' a term exactly.

Consider an arbitrary polytesimal $j$:

$$
j =
... + k_{n-1} \epsilon^{n-1} + k_n \epsilon^n + k_{n+1} \epsilon^{n+1} + ...
$$

We find that:

$$
\begin{aligned}
\mathrm{zoom}_{n-1} (j) &= k_n \epsilon + k_{n+1} \epsilon^2 + ...
\\
\mathrm{zoom}_{n} (j) &= k_{n+1} \epsilon + ...
\end{aligned}
$$

Thus:

$$
\begin{aligned}
\mathrm{zoom}_{n-1}(j) &= k_n\epsilon + \epsilon \cdot \mathrm{zoom}_n(j)
\\
&= \epsilon \left( k_n + \mathrm{zoom}_n(j) \right)
\end{aligned}
$$

Therefore:

$$
k_n\epsilon &= \mathrm{zoom}_{n-1}(j) - \epsilon \cdot \mathrm{zoom}_n(j)
$$

So if $j_n$ is the $n$th term of the polytesimal $j$, then we can reconstruct it exactly by taking the difference of $\mathrm{zoom}$ levels and multiplying back up to the appropriate infinitesimal power:

$$
\begin{aligned}
j_n &= \epsilon^{n-1} \left( \mathrm{zoom}_{n-1}(j) - \epsilon \cdot \mathrm{zoom}_n(j) \right)
\\
&= \epsilon^{n-1} \mathrm{zoom}_{n-1}(j) - \epsilon^n \cdot \mathrm{zoom}_n(j)
\end{aligned}
$$

We will dub this the $\mathrm{select}$ operation, such that $\mathrm{select}_\epsilon^n$ always returns the $n$th term of the polytesimal with respect to $\epsilon$.
<!-- #endregion -->

### Substandard numbers and the substantiation operation

Given that the standard part of a polytesimal must be zero, it is apparent that applying the standard part function necessarily destroys all of a polytesimal's internal information (that is, the sequence of values that make up its coefficients). It would be good to have some means of 'realising' the value of a polytesimal while preserving its internal structure.

We have observed that every infinitesimal has a corresponding transfinite defined as its reciprocal. Intuitively, any number multiplied by its reciprocal is unit, but infinitesimals deliver the same intuition by an alternate route involving limits. We can visualise an infinitesimal 'getting smaller' as its corresponding transfinite 'gets larger' and imagine the two trends cancelling out at infinity. If these two trends, however, are even slightly 'out of step', the result is not one but potentially any number between zero and infinity.

We can harness this behaviour to define a an operation that produces, for every number $k\epsilon$ (where $k$ is real and $\epsilon$ is infinitesimal), a number infinitesimally closer to $0$ than $k$ - i.e. a number whose standard part is $k$ and whose non-standard part is an infinitesimal deflection in the direction of the origin. What's more, we can define this operator so that the non-standard part contains information that allows the original infinitesimal to be reconstructed.

If real numbers are 'standard', the numbers we are trying to build here could be termed 'substandard', and the operation that produces them from the appropriate infinitesimal could be termed 'substantiation'.

To define our operator, we need only produce for every $\epsilon$ a transfinite number $\Omega_\epsilon$ such that $\Omega_\epsilon \epsilon$ is guaranteed to be infinitesimally close to, but less than, $1$:

$$
\Omega_\epsilon = \frac{1 - \epsilon}{\epsilon} = \frac{1}{\epsilon} - 1
$$

$$
\Omega_\epsilon \epsilon = \frac{\epsilon}{\epsilon} - \epsilon \stackrel{<}{\approx} 1
$$

Multiplying any number $a\epsilon$ by $\Omega_\epsilon$ thus induces the desired behaviour:

$$
k \epsilon \cdot \Omega_\epsilon = \frac{k \epsilon}{\epsilon} - k \epsilon = k - k \epsilon = k (1-\epsilon)
$$

$$
|{k (1 - \epsilon)}| \stackrel{<}{\approx} |k|
$$

Dividing by the same, of course, retrieves the original value $a\epsilon$.

In the context of polytesimals, we introduce an operator $\mathrm{sst}$ that is given to perform all these steps. When the 'infinitesimal base' is not notationally self-evident, we will allow the operator to be subscripted with the intended base, e.g. $\mathrm{sst}_\epsilon$ would be pronounced 'sub with respect to $\epsilon$'.

The $\mathrm{sst}$ operator is very useful for dissecting polytesimals. Applied to any one term, it retrieves a value that has the exact potency of the coefficient while effectively attaching the infinitesimal base as metadata. We must however give some consideration to how the higher powers are treated. Does $\mathrm{sst}$ act via $\epsilon^2$ when applied to $a\epsilon^2$, or simply $\epsilon$?

It turns out that we can transform any number $a\epsilon^n$ into a substandard value with the desired properties simply by applying $\mathrm{sst}$ exactly $n$ times:

$$
\begin{aligned}
\mathrm{sst}_\epsilon (k\epsilon^n)
&= k\epsilon^n \cdot \Omega_\epsilon
= k\epsilon^n \left( \frac{1}{\epsilon} - 1 \right)
\\
&= k \left( \frac{\epsilon_n}{\epsilon} - \epsilon_n \right)
= k \left( \epsilon^{n-1} - \epsilon^n \right)
\\
&= k \epsilon^{n-1}(1 - \epsilon)
\end{aligned}
\\
\begin{aligned}
\mathrm{sst}_\epsilon (k \epsilon^{n-1}(1 - \epsilon) )
&= k \epsilon^{n-1}(1 - \epsilon) \cdot \Omega_\epsilon
= k \epsilon^{n-1}(1 - \epsilon) \left( \frac{1}{\epsilon} - 1 \right)
\\
&= k \epsilon^{n-1}(1 - \epsilon) \frac{1 - \epsilon}{\epsilon}
\\
&= k \epsilon^{n-2}(1 - \epsilon)^2
\end{aligned}
$$

If we take $\mathrm{sst}^m$ to denote $m$ repeated applications, it is evident that:

$$
\mathrm{sst}^m (k \epsilon^n) = k \epsilon^{n-m}{(1 - \epsilon)}^m
$$

Thus $\mathrm{sst}^n(k\epsilon^n)$ produces $k(1 - \epsilon)^n$: a value with the 'real force' of $k$ but carrying the infinitesimal metadata of having formerly been the nth term of a polytesimal.

The formula remains valid even if $m$ is greater than $n$ (i.e. if we apply to $\mathrm{sst}$ to a number that is already 'substandard'); in such cases we effectively 'overload' the number into the transfinites:

$$
\begin{aligned}
\mathrm{sst}^2(k\epsilon)
&= k\epsilon^{-1}(1 - \epsilon)^2
= k \frac{1 - \epsilon}{\epsilon}(1-e)
\\
&= k \Omega_\epsilon (1 - \epsilon)
\end{aligned}
$$

So far, we have only tried $\mathrm{sst}$ on single terms. The operator's multiplicative nature implies that it distributes over addition. Thus:

$$
\begin{aligned}
\mathrm{sst}(a\epsilon + b\epsilon^2 + ... + k\epsilon^n)
&= \mathrm{sst}(a\epsilon) + \mathrm{sst}(b\epsilon^2) + ... + \mathrm{sst}(k\epsilon^n)
\\
&= a(1-\epsilon) + b\epsilon(1-\epsilon) + ... + k\epsilon^n(1 - \epsilon)
\end{aligned}
$$

In tandem with the $\mathrm{select}$ operator defined earlier, $\mathrm{sst}$ allows us to select the $n$th coefficient of any polytesimal in a metadata-preserving way.

Before we proceed, we should take a closer look at exactly what sort of 'metadata' is being attached to our 'substandard' numbers. Recalling that we always end up with something of the form $k(1 - \epsilon)^n$, it is apparent that the nonstandard part, after $k$ is divided out, must take the form of a binomial series (i.e. a series whose coefficients can be drawn from Pascal's Triangle). Because such a series is necessarily a sum of powers of $\epsilon$, it is itself a polytesimal: thus we can define a substandard number, more specifically, as a real number tagged with a polytesimal that, after being proportially reduced by $k$, can be factored as $(1 - \epsilon)^n$ where $\epsilon$ is an infinitesimal.


### The nuances of genre


Polytesimal 'genre' is slightly more subtle than we have made it out to be thus far. Consider the case where the genre of polytesimal $\alpha$ is another polytesimal, $\beta$, whose genre is $\gamma$:

$$
\begin{aligned}
\beta &= 2\gamma + 3\gamma^2 + 5\gamma^3
\\
\alpha &= \beta^2 + 4\beta^5
\end{aligned}
$$

We can immediately see the opportunity for a polynomial expansion:

$$
\begin{aligned}
\alpha = & \ (2\gamma + 3\gamma^{2} + 5\gamma^{3})^{2} + 4(2\gamma + 3\gamma^{2} + 5\gamma^{3})^{5}
\\
= & \ 12500\gamma^{15} + 37500\gamma^{14} + 70000\gamma^{13} + 87000\gamma^{12} + 82100\gamma^{11} \\ & + 58572\gamma^{10} + 32840\gamma^{9} + 13920\gamma^{8} + 4480\gamma^{7} + 985\gamma^{6} \\ & + 158\gamma^{5} + 29\gamma^{4} + 12\gamma^{3} + 4\gamma^{2}
\end{aligned}
$$

So in reality, $\beta$ was not the genre of $\alpha$: ultimately, $\alpha$ and $\beta$ were cogeneric in $\gamma$. (We might say that $\beta$ was only the 'apparent genre' of $\alpha$.) The same logic repeats if $\gamma$ is itself a polytesimal, and only ends when we come to a polytesimal whose (apparent) genre is not itself a polytesimal.

If polytesimal genres cannot be directly based on polytesimals, how do we construct genre bases that are guaranteed to be produce a unique monad?

There are in fact vast families of infinitesimals which support this behaviour, but given that so much depends on guaranteeing the 'incompatibility' of polytesimals, we should consider a more organised approach.

Assume we have access to a 'root infinitesimal', $\alpha$. We know that we can generate a genre of polytesimals directly off of $\alpha$ to form $\mathbb{\alpha}$. What we require is a toolkit of 'genre constructors' that accept genres and return related, but incompatible genres. With such a toolkit, we can not only construct arbitrary genres, but systems of genres with interesting properties between them.


#### The trivial constructor

Since every genre is defined by a choice of infinitesimal base, and since every polytesimal contains infinitely many copies of this base, the first thing it might occur to us to do is to define a kind of 'trivial constructor' that takes any known polytesimal and reconstructs the genre it was sourced from.

This is the point at which it makes sense to prescribe semantics for the bare $\mathbb{J}$ symbol (i.e. without a subscript). We declare that for every polytesimal $p$ and infinitesimal base $\alpha$:

$$
\mathbb{J} \left( p \in \mathbb{J}_\alpha \right) = \mathbb{J}_\alpha
$$

It might seem that $\mathbb{J}$, thus defined, overlaps with $\mathrm{poly}^\infty$ - already a somewhat incredible operation - but in fact it goes further than that: whereas $\mathrm{poly}$ expects an infinitesimal base to be provided, $\mathbb{J}$ conceptually 'tries every one' until identifying one that works.

To actually 'program' the logic of $\mathbb{J}$, one would need to devise some sort of converging sequence that can be safely terminated at a certain depth without perverting any of the desired properties of the resulting genre and its members. We will leave that as an exercise for the reader (or more likely for ourselves at a much later date).


#### Subgenres

The next constructor we propose takes an arbitrary polytesimal $p$ of a given genre $\mathbb{J}_\alpha$ to produce a new 'subgenre', $\mathbb{J}_\beta$, where:

$$
\beta = \alpha^{1/p} = \sqrt[p]{\alpha} \ , \quad p \in \mathbb{J}_\alpha
$$

We will shortly see how $p$ in this formula can be any valid polytesimal in $\mathbb{J}_\alpha$, but let's consider an edge case first: the 'trivial polytesimal $\mathbb{J}[1] = \alpha$.

$$
\beta = \alpha ^ {1 / p} = \sqrt[\alpha]{\alpha}
$$

The genre $\mathbb{J}_\beta$ could thus be called the 'trivial subgenre' of $\alpha$.

Let us take a moment to consider what $\beta$ actually amounts to here. We know that $\alpha^2$ is infinitely smaller than $\alpha$, and $\alpha^3$ is infinitely smaller still. We also know that $1 / \alpha$ is infinitely large (technically 'transfinite'): thus $\alpha$ to the power of $1 / \alpha$ is a number so small that it is effectively an infinitesimal even from the perspective of the polytesimals of $\mathbb{J}_\alpha$.

In the same way that infinitesimals 'preserve' information through real arithmetic because the reals are 'too coarse' to influence them, the polytesimals of $\mathbb{J}_{\sqrt[\alpha]{\alpha}}$ are much too 'fine' for the values of $\mathbb{J}_\alpha$. Even 'the smallest' (non-nil) polytesimal of $\mathbb{J}_\alpha$ - crudely put, $\alpha^\infty$ - is infinitely large by comparison, because the transfinite represented by $1 / \alpha$ is incomparably larger than 'natural' infinity.

--- INCOMPLETE ---

The logic is the same no matter what polytesimal of $\alpha$ we choose for the subgenre base. All such subgenres generated thereby are not only 'unreachable' by the polytesimals of their supergenre: they are also mutually unreachable. Consider two polytesimals in $\mathbb{J}_\alpha$, $p$ and $q$.

--- INCOMPLETE END ---

Writing nested polytesimals is sure to become a chore. We can avert notational catastrophe with some new syntax:

$$
\mathbb{J}_{\alpha} / p \ , \quad p \in \mathbb{J}_\alpha
$$

A polytesimal of this genre would look like this:

$$
k_1 \epsilon^1 + k_2 \epsilon^2 + ... + k_\infty \epsilon^\infty \ , \quad \epsilon = \sqrt[p]{\alpha}
$$

One can easily imagine repeating this whole process to produce a 'sub-subgenre', but the notation gets increasingly cluttered. Since a polytesimal is characterised entirely by its coefficients and its infinitesimal base - and the base is already constrained to be identical to the parent genre's base - we can borrow the matrix notation we adopted for retrieving polytesimals from genres to denote the retrieval of subgenres. To avoid conflating the two, we will use curved-bracket matrices for subgenres while retaining square-bracket matrices for polytesimals.

$$
\mathbb{J}_\alpha
\begin{pmatrix} a & b & c \end{pmatrix}
= \mathbb{J}_\alpha /
\left(
\mathbb{J}_\alpha \begin{bmatrix} a & b & c \end{bmatrix}
\right)
$$

The subgenre $(d, e, f, g)$ of the subgenre $(a, b, c)$ of $\alpha$ can then be represented concisely as:

$$
\mathbb{J}_\alpha
\begin{pmatrix} a & b & c \end{pmatrix}
\begin{pmatrix} d & e & f & g \end{pmatrix}
$$

It is immediately apparent that subgenres, defined this way, have the power to 'bundle' rich data into the terms of a polytesimal in a manner that is effectively 'orthogonal' to the polytesimal's own 'surface level' data (i.e. its sequence of coefficients). This same fact also implies a relationship between polytesimals and polytesimal genres that should allow us to convert between them.

For example, consider the genre $J = \mathbb{J}_\alpha \begin{pmatrix} a & b & c \end{pmatrix}$. If we take the 'trivial' polytesimal $J[1]$ from this genre (that is, the polytesimal which is equal to its own infinitesimal base), we find it has the value $\alpha^{1/(a\alpha + b\alpha^2 + c\alpha^3)}$. If we then take a ratio of logarithms, we can retrieve the polytesimal 'behind' the genre:

$$
\frac{\ln{\alpha}}{\ln{J[1]}} = a\alpha + b\alpha^2 + c\alpha^3
$$

Let us dub this the $\mathrm{base}$ operation, which accepts a subgenre and returns its polytesimal. Like the other polytesimal operators we've defined, we'll allow subscripts to specify the infinitesimal we are operating in respect to - e.g. $\alpha$ in the preceding example. (Since the operator is not closed - it consumes objects of one type and produces objects of another - we cannot also support repeated application like we did with the others.)

Armed with subgenre constructor $\mathbb{J}_x / y$ and the $\mathrm{base}$ operator, we now have the means to 'bundle' information into a genre and to retrieve that information on demand from any polytesimal of that genre.


#### Trivial subgenre

We will quickly touch on an interesting edge case of subgenre construction.

It will be recalled that every genre $\mathbb{J}_\alpha$ includes a 'trivial polytesimal' $\mathbb{J}_\alpha[1] = \alpha$. Consequently $\alpha$ itself is a valid subgenre base for $\mathbb{J}_\alpha$.

The resulting genre could be called the 'trivial subgenre' of $\alpha$. It makes a neat illustrative case:

$$
\mathbb{J}_\alpha(1)
= \mathbb{J}_\alpha / \mathbb{J}_\alpha[1]
= \mathbb{J}_\alpha / \alpha
= \mathbb{J}_{\sqrt[\alpha]{\alpha}}
= \mathbb{J}_{\alpha^{1 / \epsilon}}
$$

asdf


#### The root genre

Having now introduced the notion of subgenres, it may be asked what, if any, is the 'root genre'? The answer we propose for this question will imply a neat solution to a definitional impasse we glossed over before.

Earlier, we ruled that a genre cannot be based on a polytesimal. This seemingly simply proscription runs afoul of the 'trivial polytesimal' - that whose sequence of coefficients is exactly $[1]$. Such a polytesimal is equal to its own infinitesimal base, which means - in principle - any infinitesimal can be interpreted as a polytesimal, and thus no infinitesimal can be used as a genre base.

In truth, since it can never really be known in advance whether any given subscript of $\mathbb{J}$ denotes a polytesimal or not, the distinction was already a shaky one. The fact is that the genre system relies on the maintenance of strict hierarchies of infinitesimals and a presumption of incompatibility between them. If this presumption should break down, apparently valid operations may collapse into gobbledegook.

We can cut through the hierarchy of infinite regress by imagining the existence of an 'ultimate infinitesimal' that is unreachable by any method of construction at our disposal. We will name this infinitesimal $\pmb\odot$, pronounced 'sol' and rule that it is always infinitely smaller than any other infinitesimal within the scope of action.

The introduction of $\pmb\odot$ allows us to do move beyond 'arbitrary infinitesimals' and, as it were, concentrate the arbitrariness in one place. Starting with the genre $\mathbb{J}_{\pmb\odot}$ - that is, the set of polytesimals of the form $k_1 \pmb\odot ^ 1 + k_2 \pmb\odot ^ 2 + \dots$ - we can use the subgenre constructor to create as many new genres as we like.

While 'arbitrary infinitesimals' remain useful in this definitionl stage, later on we will see how the concept of $\pmb\odot$ permits vast networks of genres to interrelate in a common framework, with implications for a more computational view of polytesimals.


#### Hadamard genres

We have just devised an unary constructor that acts on genres to produce subgenres. Can we conceive of an 'ennary' constructor that in some sense 'combines' multiple genres to create a new 'product' genre?

Given that all polytesimals have the same cardinality (that of the naturals $\mathbb{N}$), we have the option to perform elementwise multiplication - that is, to take the Hadamard product. If we do this over a set of polytesimals that share a genre, the result will simply be another (smaller) polytesimal in the same genre. However, if we perform the same operation on nongeneric polytesimals, the resultant polytesimal must be of a new genre because the product of two incompatible infinitesimals is necessarily a third infinitesimal incompatible with the other two.

The Hadamard product on matrices is usually denoted with $\circ$, to distinguish it from the other kinds of product. We can extend $\mathbb{J}$ to support this notation:

$$
\mathbb{J}_\alpha \circ \mathbb{J}_\beta = \mathbb{J}_{\alpha \cdot \beta}
$$

We can draw a polytesimal from the resulting genre in the usual way:

$$
\mathbb{J}_{\alpha \cdot \beta}[a, b, c]
= a\alpha\beta + b\alpha^2\beta^2 + c\alpha^3\beta^3
$$

An interesting thing happens if we try to divide such a polytesimal by one of the two infinitesimals:

$$
\frac{a\alpha\beta + b\alpha^2\beta^2 + c\alpha^3\beta^3}{\beta}
= a\alpha + b\alpha^2\beta + c\alpha^3\beta^2
$$

The first part, $a\alpha$, remains a legitimate polytesimal. It unclear what to make of the sum of the rest of the terms unless we broaden our conception of what a polytesimal can be.


#### Product genres and multigeneric polytesimals

When dealing with conventional polynomials, we are familiar with expansions of the form:

$$
\begin{aligned}
(a + b)^2 &= a^2 + 2ab + b^2
\\
(a + b)^3 &= (a^2 + 2ab + b^2)(a + b)
\\
&= a^3 + a^2b + 2a^2b + 2ab^2 + ab^2 + b^3
\\
(a + b)^4 &= \dots
\end{aligned}
$$

Thus far we have imagined polytesimals only as sequences of powers of a single infinitesimal base. Such 'monogeneric' polytesimals could be viewed as only a special case of a more inclusive family: one which encompasses 'multigeneric' polytesimals as well.

Consider two (incompatible) infinitesimal bases, $\alpha$ and $\beta$. A monogeneric polytesimal comprises the sum of every natural power of its base greater than zero. A multigeneric polytesimal over $\alpha$ and $\beta$, by analogy, should be expected to contain every combination of powers of its constituent bases: in other words, the Cartesian product of the two sequences.

We can notate this directly using the standard $\times$ symbol:

$$
J = \mathbb{J}_\alpha \times \mathbb{J}_\beta
$$

If we want to retrieve a polytesimal from this genre, it is not enough to supply a flat sequence of coefficients: we must provide a coefficient for every pair of powers. The significance of adopting matrix notation for polytesimal retrieval should now be evident. If we imagine labelling each column of the matrix with a power of $\alpha$ and each row with a power of $\beta$, we can write:

$$
p = J \begin{bmatrix}
a & b \\
c & d
\end{bmatrix}
= a\alpha\beta + b\alpha^2\beta + c\alpha\beta^2 + d\alpha^2\beta^2
$$

The same logic extends to subgenre creation:

$$
\mathrm{base} \left( J \begin{pmatrix}
a & b \\
c & d
\end{pmatrix}
\right)
= p
$$


### Polytesimal spaces

Though we omit the 'void' terms for brevity, polytesimals are in principle infinitely long. If we take just the sequence of coefficients, we have an object that maps the natural numbers to the reals. In other words, polytesimals can be represented as vectors in an infinite-dimensional space.

When try to cast regular polynomials (e.g. $ax^{2} + bx$) into coefficient space, the mapping of points to values is non-unique (i.e. there are infinitely many ways to make $ax^{2} + bx = 2$ for any value of $x$). Due to the nature of infinitesimals, our polytesimals behave differently. Whereas a pair of standard polynomials may have different coefficients and still be equal, two polytesimals are only equal if their coefficients are identical. We can imagine ordering every polytesimal sharing the same genre to a number line - the 'generic number line' - which is a lexicographical sorting of the set of infinite sequences of reals $\mathbb{R}^\mathbb{N}$, sharing the cardinality of $\mathbb{R}$.

This 'generic number line' is just $\mathbb R^{\infty}$ in another guise, and the infinite array of infinitesimals it designates can therefore be cast without conflict to infinite real space. Essentially, we can map one-to-one from points on the 'generic number line' to points in real space, and vice versa. can produce infinitely many unique infinitesimals just by 'plucking' them out of real space: and more, the 'genre' of infinitesimals we produce in this way can be 'prestructured' because it is derived from points in real space that can be structured.

If the set of cogeneric polytesimals falls on a number line (which can itself be viewed as an infinite vector), how can we make sense of the 'space of all polytesimals' regardless of genre? This is much harder to wrangle because we don't have a strong grasp of what the 'set of genres' looks like. We can nevertheless make one useful observation, which is that the 'null polytesimal' is shared between all genres (since it has no non-standard part to speak of). Viewed spatially, this is akin to saying that the 'origin' $(0, 0, 0...)$ is shared by all polytesimal spaces, regardless of genre.


## Scaffolds


We have been on a long journey through some deeply non-standard maths. Thankfully, we are closing in on a formalism and a methodology that will allow us to represent arbitrary, rich objects in a common mathematical framework.

We now introduce the concept of the 'Scaffold'. A Scaffold is a kind of arbitrary structure that can be attached to the Pleroma to permit us to more easily 'build' things in it - hence the name. We are going to establish a general pattern for producing Scaffolds and show how they can be applied to the Pleroma to create what we will call a 'Cosmos' - a rich ordering of space that is ready for Schemas to adopt as a Domain.

To build up our Scaffold, we'll need to develop a few more 'tricks'.


### Scoping the problem


The Pleroma has plenty of space, but it doesn't have very much structure. Because it is defined as the symmetric product, not only are its dimensions without order: they are also without *identity*.

For example, take two arbitrary points, $A$ and $B$. Since there is no ordering, coordinates must be represented as sets - and since there is nothing forbidding points having the same value on multiple axes, we need multisets - that is, sets permitting duplicates (sometimes called 'bags' in data science).

Since we're using uppercase Roman letters to name the points, we'll use lowercase Roman letters to name the (real-valued) components:

$$
\begin{aligned}
A &= \{a, b, c, 0, 0, ...\} 
\\
B &= \{d, e, f, g, 0, 0, ...\}
\end{aligned}
$$

The sets are in principal infinitely long - padded with zeros (specifically, Void values) for all the 'inactive' dimensions.

Now, it is axiomatic to being a 'point' that there must be one dimension provisioned for each value in each coordinate. So we can see that $A$ requires three active dimensions (one for each of $a$, $b$, and $c$) and $B$ requires four (for $d$, $e$, $f$, and $g$).

The question is, how many dimensions do we require to represent *both points*?

The temptation is to say 'four', because we could 'borrow' three of the dimensions from $B$ to represent $A$. This, however, is only one way we could validly allocate dimensions across these sets. We *could* allocate as many as seven, and for any number less than that, there is a combinatorial explosion of *ways* that those dimensions could be allocated: some putting $a$ and $d$ on the same axis, some putting $f$ and $b$ on the same axis, and so on and so on. Crucially, when the dimensions lack identity, all of these dimensionalisations are equally valid, and the best we can say is that the two sets between them define a cloud of candidate point pairs, ranging from tightly bunched to widely separated. We have no means at present to be more specific than that.

What we need is some sort of policy which we can declare up front that allows us to say "For this group of points, the dimensionalisation will be such and such". This policy must be robust and universal without being overly restrictive or pedantic.

One possibility would be to order the components of each point, line up the resulting sequences, and allocate one dimension to each pair, from left to right. This gives us a dimensionalisation that is unique and maximally parsimonious, but it prevents the values from expressing themselves without that implication: values that are being used as dimensional markers are no longer free to use in other ways.

What we'd really like to be able to do is to take arbitrary values, like $a$ and $b$, and 'tag' them with dimensional metadata - but in a way that does not layer new mechanics over the Pleroma or challenge its inherently symmetrical qualities.


### Real tagging


Let's imagine that we have some function $f$ that uses only addition and subtraction. Such a function is closed over the integers (i.e. if we only ever feed in integers, we will only ever get out integers).

Now imagine, instead of passing in an integer, we pass in a real number whose non-integer part is extremely small (e.g. $1.000000001$). It is clear that, unless we iterate $f$ many times, this non-integer part will not affect the output and can for most intents and purposes be neglected. The decimal will 'tag along' with the integers and can be used, in a sense, to 'attach metadata' the numbers that will be preserved through the operation.

$$ 2 + 3.001 = 5.001 $$

Now, say we our function $f$ actually accepts two inputs, $x$ and $y$, producing a third, $z$. If we add a very small non-integer part to $x$, and a different, dramatically smaller non-integer part to $y$, then not only will the decimal part 'travel through' the function with altering its first-order output, but the non-integer parts will not even interact with each other:

$$ 2 + 3.001 + 5.00001 = 10.00101 $$

In a sense, we could say that we have 'tagged' each value. What's more, we have tagged them uniquely so that different tagged values can interact without disrupting each other (up to a point). The resultant value, $10.00101$, functions adequately as the number $10$ with some error, while containing metadata in its fractional part that reveals the path that was used to construct it: only the sum of a $2$, a $3$, and a $5$ could produce that exact pattern of decimals.

When it comes to integers and reals, this 'tagging' trick is just that - a trick - and an unreliable one at that. We are forbidden from multiplying or dividing our values without disrupting the tags, and if we add more than a hundred of any one value (whether all at once or consecutively), we are going to have a 'buffer overflow' (the decimal part representing $5$, say, will overlap with the decimal part representing $3$).

In the Pleroma, however, we are not dealing with finitary values like reals and integers. The Pleroma uses the hyperreals. In the same way that real numbers can preserve metadata through integer functions, hyperreal numbers can preserve metadata through real functions. Better still, because of the unique properties of infinitesimals as opposed to decimals, we can actually preserve much more metadata with much richer structure, and preserve it through much more complicated transformations.


### Hyperreal tagging


Let us again represent arbitrary infinitesimals with lowercase Greek letters. We can combine these with real values (lowercase Roman letters) to produce hyperreal values that are distinguishable from each other but indistinguishable from their real parts.

$$
a + \alpha \ne a + \beta
\\
\mathrm{st}(a + \alpha) = \mathrm{st}(a + \beta) = a
$$

Now say we have three hyperreal values, $A$, $B$, and $C$:

$$
A = a + \alpha
\\
B = b + \beta
\\
C = c + \gamma
$$

What happens when we pass these values through some basic arithmetic?

$$
\begin{aligned}
C(A + B) =& \ (c + \gamma)(a + b + \alpha + \beta)
\\
=& \ ac + bc + c\alpha + c\beta + a\gamma + b\gamma + \alpha\gamma + \beta\gamma
\end{aligned}
$$

In the expansion, we have two real terms, four hyperreal terms, and two infinitesimal terms. If we take the standard part of the whole expression (dropping all but the real terms), we find:

$$
\mathrm{st}(C(A + B)) = \mathrm{st}(c(a + b))
$$

The result, of course, is a real number: exactly the same real number we would have got to without the infinitesimals. Yet if we focus in on the non-standard part instead, we find that the result has carried the history of the operation with it. We can see that $\alpha$, $\beta$, and $\gamma$ are all present, and will remain present no matter how much addition or subtraction we do: whatever metadata these values encode is safe.

However, we also introduced multiplication to the chain of operations, and this has resulted in a pair of infinitesimal terms at the end. If $\alpha$, $\beta$, and $\gamma$ are cogeneric polytesimals, then these two trailing terms would combine into one big new polytesimal, $\delta$, which would also be cogeneric with the others. We have generated some 'new information': we haven't yet decided what it 'means'.

Thus far we have attached our 'hyperreal tags' using addition. Can we use multiplication instead? In the case of real-valued tags, the answer no: however, the hyperreals are much more flexible.

Recalling our notation for 'unit polytesimals' introduced earlier (where each value is an infinitesimal perturbation on the value of one):

$$
a \breve{\alpha} = a (1 + \alpha) = a + a\alpha
$$

After tagging, we still have a standard part and a non-standard part, and (assuming that $a$ does not secretly carry any infinitesimals inside) the only change from simply attaching the tag with addition is that the non-standard part has been rescaled in the magnitude of $a$. So long as any 'metadata' in $\alpha$ is carried in the relative proportions of the coefficients, and not in their absolute value, we have lost nothing.


### Polytesimals as unit vectors

We observed earlier that polytesimals of a given genre can be interpreted as coordinates in an infinite-dimensional, real-valued space. Crucially, the dimensions of this space are ordered and identifiable, unlike the dimensions of the Pleroma.