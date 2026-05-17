# Gospel language reference

Gospel is an experimental micro-language native to the Everest 'science OS' ecosystem. Its purpose is threefold:

- To provide 'reference implementations' for simple programs written in other codes.
- To define small, portal blocks of precision logic that can be defined in one place and executed reliably in another.
- To aid in the formalisation for other systems and frameworks in the ecosystem.

## Core syntax

Everything in Gospel 'expresses something' (``<expr>``), sometimes with side-effects.

### Atomic expressions

Atomic expressions or 'literals' (``<lit>``) are standard ``int``, ``str``, ``float``, and ``bool`` types.

Identifiers (``<ident>``) are special strings complying with the rules restricting Python variable names. Many strings in Gospel are required to be valid identifiers so they can be accessed via Python-style 'dot notation' from other objects, e.g. ``foo.bah``. An identifier used outside of the context of dot notation is always assumed to be a reference to a syntactic keyword of some kind (e.g. ``tuple``).

Strings that are not identifiers must be wrapped in ``'`` characters. Identifier-type strings may or may not be wrapped at the user's discretion (e.g. ``foo."bah"`` is acceptable). There is no escaping for internal ``'`` characters.

There is also an ``undefined`` literal, whose purpose is to thwart comparisons with any other object - i.e. ``undefined == foo`` is always ``undefined``.

### Parenthetical expressions

Any expression can be wrapped in round brackets (``(...)``) without changing its value whatsoever. Parentheses are used to disambiguate syntax and make code more readable. They have no special function beyond this.

Since everything in Gospel is an expression, and expressions must always evaluate to something, the behaviour of ``()`` (i.e. with no content) must be stipulated. Gospel considers an 'empty expression' to have the value of ``undefined``; thus ``()`` is available as a syntactic shorthand for ``undefined``.

### Container expressions

Gospel supports one kind of container: an immutable multiset (a set which can have duplicate members).

The most basic container operator is the unary prefix `+` operator, pronounced 'promote'. This takes any object and produces the singleton set containing only that object.

Non-trivial containers are produced by combining pre-existing containers using the binary infix operators ``&`` for intersection, ``|`` for union, and ``~`` for difference.

The ``&`` and ``|`` operators support an unary prefix mode: the argument is expected to be a container of containers and the chosen operator is applied recursively to every pair of members of that container; i.e. ``|(++a | ++b) => (a, b)``. The result of applying either to an empty container is the container itself.

The difference operator ``~`` also has an unary prefix form, which is syntactic sugar for ``univ ~<container>`` (see next section).

Attempting to promote ``undefined`` results in the empty set. Consequently there is no constructive method to create a container with ``undefined`` as a member. Gospel canonises this behaviour by ensuring that it applies inductively as well: any operation in Gospel that returns a container automatically ejects any ``undefined`` members before returning. This behaviour will become very useful later on.

#### Special containers

There are several 'built in' containers that can be retrieved at any time by keyword. We have already encountered one - ``univ``; now here are the others:

- ``null`` is the empty set
- ``univ`` contains all legal objects in Gospel (one copy each)
- ``ints`` contains all integers (one copy each)
- ``nats`` contains all integers greater than or equal to zero (one copy each)
- ``bools`` contains ``True`` and ``False`` (one copy each)

Special containers power special container tricks.

A conventional set (i.e. without duplicates) can be produced from any container by taking the intersection of container with the special ``univ`` container, which (conceptually) 'contains' exactly one of everything. The result is still technically a container and therefore technically a multiset, but one that happens to be without duplicate members.

#### Implicit containers

Some containers can be defined but not enumerated.

For example, consider the union of the container ``(+1 | +1 | +2)`` with ``univ``. The result is, logically, a container that contains 'one of everything' as well two extra copies of ``1`` and one extra copy of ``2``. Such an entity is comprehensible and amenable to analysis, but is clearly not enumerable.

Likewise, the container ``univ ~ +1`` is a container containing 'everything except 1'. In contexts where that is all we need to know, the fact that the container is not enumerable is not a problem. In other contexts, it may be a program-breaking problem.

Such 'implict containers' are treated like regular containers as far as possible. Attempts to build expressions out of implicit containers when explicit containers are required resolve to ``undefined``.

#### Container cardinality

There are many conceivable situations in which it will be important to know 'how big' a given container is. For this purpose, the unary prefix ``len`` operator is provided. The sole operand of ``len`` is expected to be a container, and the value of the expression is always a natural number (a subclass of ``int``). Invalid arguments for ``len`` return ``undefined``.

### Arithmetic expressions

Gospel supports the standard binary arithmetic operators ``add`` and ``mul``, as well as the unary operators ``neg`` and ``rec`` (for negation and reciprocation respectively). These operators act intuitively on numerical values of type ``int`` or ``float``; when all the operands are ``int``, the expression returns ``int``, otherwise ``float``. However, if any of the operands of an arithmetic expression is ``undefined``, the result is also ``undefined``.

The ``add`` and ``mul`` operators support unary prefix modes as well. These function similarly to the container operators, providing an easy way to get the sum or product of the members of a container. Applying ``add`` to an empty container produces ``0``, and applying ``mul`` to an empty container produces ``1``.

When any argument of any arithmetic operator is ``undefined``, the result is also ``undefined``.

### Boolean expressions

Any expression in Gospel can be interpreted as a boolean (``True`` or ``False``). The behaviour follows Python conventions: numerical values of zero, empty strings, and empty containers are all ``False``, while everything else is ``True``. The ``undefined`` literal evaluates to ``False``. Values are implicitly cast to booleans by the system when required.

Boolean arithmetic is supported:

- **Rich comparison**: the operators ``==``, ``~=``, ``<``, ``>``, ``<=``, ``>=`` are supported for ``int``, ``float``, ``str``, ``container`` types, and function analogously to Python.
- **Boolean operators**: when applied to non-containers (i.e. ``int``, ``str``, ``float``, ``bool``, ``undefined``) ``&`` and ``|`` serve as 'and' and 'or' operators. There is also an unary prefix 'not' operator ``~`` i.e. ``~True == False``. When the operands are not boolean, they are cast to booleans first.

The ``==`` and ``~=`` operators support an unary prefix mode. The argument is expected to be a container, and the result is as if one applied the operator in binary mode recursively to the members of the container. For example, ``==a`` returns ``True`` if all the elements of container ``a`` are the same. Applying ``==`` to an empty container evaluates ``True``, and applying ``~=`` to an empty container evaluates ``False``.

When any argument of any boolean operator is ``undefined``, the result is also ``undefined``.

### Querying

Some objects have accessible 'content'. Content can be retrieved using the binary infix query operator ``.``: e.g. ``foo.bah`` indicates the retrieval of the content associated with the identifier-type string ``bah`` from the object ``foo``.

Literals are thought of as having the content of ``True`` when queried with a value equal to themselves, otherwise ``False``: e.g. ``(1).1 == True`` (note the use of parentheses to avoid inadvertently producing a ``float`` here).

Querying containers effectively 'distributes' the query over each member of the container. The result is a new container whose members are the results of each sub-query: ``(+a | +b | +c).a == + True | + False | + False)`` (Note that non-enumerable containers return ``undefined`` if operated on in this way.)

Attempts to retrieve ``undefined`` or retrieve from ``undefined`` result in ``undefined``. Attempts to retrieve something that does not exist also return ``undefined``.

### Query composition

Querying (using ``.``) is the principle means in Gospel of 'getting information out of something'. It is helpful to be able to chain such requests together. This functionality is provided with the binary infix 'compose' operator ``@``. The object returned by ``@`` is called a 'composition'. When queried, the query is first passed to the right-hand operand, then the result of that query is passed to the left-hand operand, and the result returned:

```
(foo @ bah).qux == foo.(bah.qux)
```

Since all objects in Gospel support querying, all objects are valid arguments for compositions, including compositions themselves (which, as with all other binary operators, are left-associative):

```
(foo @ bah @ qux).zap == foo.(bah.(qux.zap))
```

### Conditional logic

Gospel implements conditional logic at the level of operators and expressions rather than at the level of statements and clauses.

The question mark character ``?`` implements Gospel's interpretation of 'if'. A binary infix operator, ``?`` takes on the value of its second operand if the result of casting the value of the first operand to a boolean is ``True``; if the result instead is ``False``, the whole expression evaluates to ``undefined`` and the second expression is discarded without ever being evaluated. In either case, the first value is discarded.

Paired with ``?`` is the 'else' operator, ``;``, which complements its function. A binary infix operator, ``;`` returns the value of its first expression if it is not ``undefined`` (if so, discarding the second expression without evaluation); if the first value is in fact ``undefined``, the second expression is evaluated and returned instead.

Because, like all operators in Gospel, ``;`` is right-associative, ``?`` and ``;`` operations can be strung together without parentheses to reproduce conventional if-else blocks:

```
(2 add 2 == 4) ? 'There are four lights!' ;
(2 add 2 == 5) ? 'Ignorance is strength' ;
'There is no spoon.'
```

While ``?`` and ``;`` work well together, they are also useful by themselves. The ``?`` functions as a general guard operator. The ``;`` operator effectively functions as a line delimiter if its first argument is forced to assume the value of ``undefined``. Since this can be cumbersome in practice (e.g. ``(...).();``), the ``;`` operator has a special unary postfix form which swallows the object to its left and returns ``undefined``. Since the unary form of ``;`` has a slightly higher precedence than the binary form, and both have a lower precedence than any other operator in the language, pairs of semicolons effectively constitute a single dedicated 'new line' operator:

```
'Hello';; 'world';; 'one';; 'expression';; 'at';; 'a';; 'time';;
```

### Maplets

A 'maplet' is an ordered pair of entities with the behaviour that, when queried with a value equal to the first of the pair, returns the second of the pair, else ``undefined``. A maplet is produced using the binary infix operator ``=``:

```
(a=b).a == b
```

Chains of maplets can be made much more accessible when combined into compositions:

```
((b=c) @ (a=b)).a == (b=c).((a=b).a)
```

### Type expressions

Gospel is strictly typed. Everything has a type, including types themselves, which have the type ``type``. Types have hierarchies, with every object ultimately being of type ``object``. (The type ``type`` is of type ``type``, but even it is still ultimately of type ``object``.) The type of any object can be obtained at any time by applying the unary prefix ``t`` operator (e.g. ``t 1 == int``), with types themselves being amenable to comparison like any other object.

Types are represented with type expressions (``<type_expr>``).

Literal types are trivially represented: ``int``, ``float``, ``str``, ``bool``, and ``undef`` are the types of integers, floats, strings, booleans, and the ``undefined`` literal. (Indeed, ``t undefined`` is the only expression involving ``undefined`` that does not return ``undefined``!)

New types can be generated from old types using 'type operators', which are all prefixed with ``t``.

The binary infix ``tadd`` operator generates sum types - that is, a type which can be either one type or another. For example, ``int tadd str`` represents a value that can be either an ``int`` or a ``str``. It supports an unary form, ``tadd (int, str) == int tadd str``.

The binary infix ``tmul`` operator generates container types. For example, ``int tmul float`` represents the type of a container that has exactly one ``int`` member and exactly one ``float`` member. It supports an unary form, ``tmul (+int | +str) == int tmul str``.

Multiples of identical types can be represented with the shorthand binary infix operator ``tmulmul``, where the right side must be a non-negative integer (e.g. ``int tmulmul2`` for containers containing two integers).

When producing new types with arithmetic operators, one must be mindful of the left-to-right nature of the language. For example, ``int tmul float tmul str`` logically does not define a three-member container, but rather a two-member container where one of the members is of type ``int tmul float`` and the remaining member is a ``str``. To define a three-member container, one would have to use the unary form of ``tmul``; e.g. ``tmul(+int | +float | +str)``. Likewise, to denote a choice between three different types, one would use ``tadd(+int | +float | +str)``.

Finally, the digraph ``->`` is a binary infix operator used to define maplet types. Thus ``t (0 = 'a') == int -> str``.

Attempts to build types out of ``undefined`` objects return ``undefined`` (not ``undef`` - that is, the 'type' of undefined).

### Publication, retrieval, and scoping

Gospel supports the storage and retrieval of arbitrary objects in an invisible 'scope object'.

Any object can be 'thrown up' into the current active scope using the 'publish' operator ``!``, which is an unary prefix operator. Published objects disappear from their current position and conceptually go 'up' into the scope where they can be retrieved in the future. The result of the ``!`` expression itself is ``undefined``.

Objects are retrieved from the current scope using the 'retrieve' operator ``$``, which, like ``!``, is an unary prefix operator. The argument of ``$`` is used to query each previously published object in the current scope in reverse publication order until one of them returns a value that is not ``undefined``. That value is then returned.

Both `$` and `!` are given relatively low precedence by the parser. This provides for some appealing syntax. For example, `!` in tandem with `=` (defining a 'maplet'), we can bind and reference arbitrary variables in a fairly conventional way:

```
!a=b ;; $a == b
```

Scopes in Gospel are nested: that is, every scope bar the 'entry scope' at program start has a 'parent' scope. If retrieval returns undefined for all objects in the current scope, the process is repeated in the next scope up, and so on up to the entry scope. While the entry scope always exists, other scopes may be created and destroyed during the life of the program. This is accomplished using the special scoping syntax ``{<expr>}``. Any publication or retrieval expressions evaluated inside ``{}`` characters act on that scope, not the enclosing scope.

```
!foo=1;; {!bah=2};; $foo mul $bah ; 'The result was undefined because $bah was in a different scope'
```

Scopes and all of their stored objects are scheduled to be destroyed as soon as the scope closes. No method is provided to preserve scopes or act on them 'from the outside', in keeping with the stateless philosophy of Gnostic.

At present, no method is provided to publish or retrieve with respect to higher scopes than the current scope.

### Lazy expressions

Many higher-level behaviours in Gospel rely on delaying the evaluation of expressions until a certain time. Gospel provides an explicit syntax for this using the `` ` `` character. This is called 'engraving'. Every operator in Gospel can be engraved with one or more `` ` `` symbols to produce an 'nth degree expression': e.g. ```2 ``add 3``` would be a 'second degree expression'. Every time an expression is evaluated, its degree is decremented by one, until the zeroth degree is reached and 'actual evaluation' occurs.

For operators that necessarily come in pairs - i.e. bracket-type operators like ``[...]`` and ``{...}`` - only the 'opening' operator (e.g. ``[`` or ``{``) needs to be engraved. (Standard parentheticals, being hyper-syntactic, have as special behaviour when engraved, as discussed below.)

Manually prefixing every operator in an expression is cumbersome, so an alternative is to use an 'engraved parenthetical' which effectively 'increments' (raises the degree of) every operator inside: e.g. `` `(2 mul 3 add 5)`` is equivalent to ``(2 `mul 3 `add 5)``. Nested parentheticals are themselves incremented; so `` `(2 mul `(3 add 5))`` is equivalent to ```2 `mul (3 ``add 5)```. Multiple 'degrees' can be specified in the expected way: e.g. ` ``(...)`. Mnemonically, though not literally, it is as if the 'engrave' operation 'distributes over parentheticals'.

### The star operator

The most important single operator in Gospel is perhaps the star operator `*`, which is pronounced 'unpack'. The general semantic sense of `*` is to destructure, decrement, progress, and compute.

#### Unpacking lazy expressions

The most powerful use of `*` is to 'unpack' - that is, 'execute' - lazy expressions:

```
!expr=(2 `mul 3);
*$expr == 6 ? 'See how that worked?'
```

The 'wave of unpacking' progresses all the way down the expression tree, decrementing every engraved operator before evaluation:

```
!expr=(2 `add 3 `mul 5);
*$expr == 17 ? 'Both operators got unpacked.'
```

The effect is the same whether the expression was engraved manually or all at once using the `#` operator:

```
!foo=`(2 mul $arg add 5);
!arg=3;
*$foo == 11 ? 'Now this is podracing!'
```

A single lazy expression can be decremented 'n' times with 'n' rounds of unpacking:

```
!foo=(2 ``mul 3 ``add 5);
**$foo == 16 ? 'Double unpacking, twice the fun.'
```

#### Looping

By binding a lazy expression to the current scope before unpacking, classic 'looping' behaviour becomes possible.

```
{*(!count=0; !expr=`($count == 5 ? 'Done!' ; (!count=($count add 1); $expr)))} == 'Done!'
```

In the above example, the argument of ``*`` is first evaluated as far as it can go, ultimately returning the lazy expression that is the logic to be looped, but with the side-effect of binding a state variable (``count``) and the logic itself (``expr``) to the current scope. The ``*`` operator then decrements the ``expr``, triggering evaluation; inside the expression, branching logic reads the state and either assumes the value of a string or defers to the fallback branch (from ``;`` on) which mutates the state and, finally, returns the original expression, exactly as it was before ``*`` took effect - but now evaluated in the context of a different value of ``count``. The whole ensemble is wrapped in ``{...}``, capturing the binding expressions so that neither ``count`` nor ``expr`` leak into the general scope, where they would have no real meaning.

#### Ragged unpacking

There are occasions when it may be desirable to mix engraving levels in the same expression. The syntax supports this directly, but some care must be taken to avoid type errors.

Consider:

```
2 `add 3 ``mul 5
```

If we unpack this expression, the ``add`` operator will decrement to execution level and attempt to resolve. The execution will fail, however, because while the first operator is a number, the second operator is an engraved expression (``3 `mul 5``), which ``add`` does not know how to work with.

Alternatively, consider:

```
!expr=(`$foo ```mul ``$foo);
!foo = 3;
!expr=*$expr;
!foo=5;
!expr=*$expr;
*$expr == 15 ?
'The first two unpackings set values for foo, the third executed mul.'
```

### Branching evaluation

It will be noted that we have not yet provided any means of extracting a single item from a container - that is, there is no equivalent 'demote' operation to match the 'promote' operation (``+``).

Gospel does in fact provide this functionality, albeit in an unconventional way which doubles as a gateway to the language's powerful branching evaluation feature.

#### The branch operator

The `%` operator, pronounced 'branch', is a prefix operator that accepts a single container as its sole operand. At the moment that a branch expression is evaluated, the flow of the program branches into $n$ threads - one for each member of the container.

Within a given thread, the branch expression evaluates to the corresponding member; evaluation then continues as normal. The thread is provisioned with a copy of every relevant scope and may continue to read from and write to that scope as usual, completely unaffected by - and indeed, unaware of - any of its sibling threads. Depending on the implementation, those threads may execute sequentially, or concurrently, or even simultaneously. All computation in Gospel happens in some thread or other, whether that be the 'entry thread' created at program initialisation, or one of a branching tree of child threads spreading from that root.

In the case of singleton containers (e.g. ``+a``), the `%` operator has the pleasing side-effect of simply 'destructuring' the container, returning `a` in the local thread. (Implementations should be smart enough to recognise that no actual branching needs to occur in this case.)

Given that containers are multisets, not sets, the behaviour of any duplicate members must be considered. Because the value of `%` provides the sole original point of difference between different branches, multiple threads descending from a common origin are redundant. Consequently, `%` produces only one thread for each unique member of its operand, with that value then serving as a natural identifier for the thread itself. (The existence of any duplicates at branch point may be tracked as metadata on the thread, depending on the implementation.)

The case of empty containers is handled in a consistent, but perhaps surprising, way. Since a container with $n$ unique members should always be relied upon to branch into $n$ threads, it follows that branching ``null`` sets the thread count to zero - i.e. it terminates execution. Thus the expression `%()` is akin to a 'halt' primitive on the current thread (whether that is the 'entry thread' or one of its subsidiaries).

#### The merge operator

When a thread is branched, it goes into hibernation until its children collaboratively settle on a single 'ground truth'.

Though threads in principle cannot communicate with each other and are conceptually unaware of each other, they are nevertheless aware of their parent thread and thus of their own place in the larger control flow. This 'branch awareness' is what allows the merge operation to be carried out.

'Merge' is an unary postfix operation symbolised by `#`. The operand can be any valid value in the language. If and when the thread is resumed (see below), the expression takes the value of the operand, whatever that may be.

At the moment that `#` is encountered during evaluation, the thread is frozen: it remains frozen until all its sibling threads are either dead or similarly frozen. (Note: a thread that is merely 'hibernating' due to its own internal branching event does *not* count as 'frozen'.)

Once all living sibling events are frozen, the merge procedure can begin. The goal of this procedure is to identify or retroactively construct a single thread that can serve as the one ground truth. Once obtained, this 'golden thread' is 'grafted' back onto the parent thread, with the new thread carrying on under the identity of the parent as if the branching had never happened.

The simplest way that the merger can be resolved is in the case where less than two threads remain alive. If no threads have survived, the parent thread simply dies, just as if it had evaluated `%()` itself. If exactly one thread survives, that thread is selected as the golden thread and grafted to the parent: the child thread's scopes overwrite the parent's scopes and evaluation continues where the child thread left off, with the sole difference that - for the purposes of future executions of `#` - the thread is now identified as its parent. This is called a 'trivial merger'.

A 'non-trivial merger' occurs when more than one thread survives to the merge point. In this case, the branch and merge values for each thread are joined into maplets and collected into a single container: the 'merge set'. Because branching ignores any duplicates in the branched container (see above), it is always possible to query the merge set such that a singleton output is produced. The responsibility for providing such a query falls on the user - or rather, on the environment. Whether arbitrarily by user choice, or programmatically by means of a (Gospel) arbitration expression, a singleton must be produced for the program to continue, otherwise the parent thread dies. The thread that produced the winning singleton is the golden thread. Non-trivial mergers are the principle means by which interactivity and concurrency are facilitated within the world of Gospel.