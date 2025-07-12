..  comment
    # Copyright 2020 The Cloud Custodian Authors.
    # SPDX-License-Identifier: Apache-2.0

..  _`integration`:

########################
Application Integration
########################

We'll look at integration of CEL into another application from four perspectives:

1.  We'll start with `Integration Essentials`_. This is the base case for integration into another application.

2.  In `Function Bindings`_, we'll look at a more sophisticated integration. This extends the environment with custom functions.
    This can provide a well-defined interface between CEL expressions and your application's functionality.

3.  `More Examples from the Go implementation`_ shows how extend the environment using new types.
    Python's use of duck typing removes some of the complexity of the Go implementation.

4.  There are a few exception and error-handling cases covered in `Exceptions and Errors`_.

5.  The `Cloud Custodian (C7N) Integration`_ is rather complicated because the C7N is covers quite a large number of distinct data types.

5.  Finally, `External API`_ will review some elements of the API that are part of the integration interface.

Integration Essentials
======================

Here's an example of variable bindings taken from a ``README`` example:

..  code-block:: python

    >>> import celpy
    >>> cel_source = """
    ... account.balance >= transaction.withdrawal
    ... || (account.overdraftProtection
    ... && account.overdraftLimit >= transaction.withdrawal - account.balance)
    ... """

    >>> env = celpy.Environment()
    >>> ast = env.compile(cel_source)
    >>> prgm = env.program(ast)

    >>> context = {
    ...     "account": celpy.json_to_cel({"balance": 500, "overdraftProtection": False}),
    ...     "transaction": celpy.json_to_cel({"withdrawal": 600})
    ... }
    >>> result = prgm.evaluate(context)
    >>> result
    BoolType(False)

The ``cel_source`` is an expression to be evaluated.
This references variables with names like ``account``, and ``transaction``.

All CEL evaluation uses an :py:class:`celpy.Environment` object.
The :py:class:`celpy.Environment` is used to provide type annotations for variables.
It can provide a few other properties, including an overall package name, sometimes needed when working with protobuf types.

The :py:meth:`Environment.compile` method creates a abstract syntax tree from the CEL source.
This will be used to create a final program to evaluate.
This method can raise the :py:exc:`CELSyntaxError` exception.

The :py:meth:`Environment.program` method creates a runner out of an abstract syntax tree.

Compiling and building a program is a two-step process to permit optimization or some other transformation the AST prior to evaluation.
The Lark parser (https://lark-parser.readthedocs.io/en/latest/classes.html) is used, and transformers are a first-class feature of this parser.

The ``context`` mapping defines variables and provides their values.
This is used to evaluate the resulting program object.
The program will produce a value defined in the :py:mod:`celpy.celtypes` module.
In this example, it's a :py:mod:`celpy.celtypes.BoolType` value.

The CEL types are all specializations of the obvious Python base types.
To an extent, these Python classes are partially based on the object model in https://github.com/google/cel-go.
We don't need all the Go formalisms, however, and rely on Pythonic variants.

Simple example using builtin types
---------------------------------------

Here's an example taken from
https://github.com/google/cel-go/blob/master/examples/README.md.
This will evaluate the CEL expression ``"Hello world! I'm " + name + "."`` with ``"CEL"`` passed as the ``name`` variable.

This is the original Go code:

..  code-block:: go

    import (
        "github.com/google/cel-go/cel"
        "github.com/google/cel-go/checker/decls"
    )

    d := cel.Declarations(decls.NewVar("name", decls.String))
    env, err := cel.NewEnv(d)

    ast, iss := env.Compile(`"Hello world! I'm " + name + "."`)
    // Check iss for compilation errors.
    if iss.Err() != nil {
        log.Fatalln(iss.Err())
    }
    prg, err := env.Program(ast)
    out, _, err := prg.Eval(map[string]interface{}{
        "name":   "CEL",
    })
    fmt.Println(out)
    // Output:Hello world! I'm CEL.

Here's the Python version, following a similar outline:

..  code-block:: python

    >>> import celpy
    >>> cel_source = """
    ... "Hello world! I'm " + name + "."
    ... """

    >>> decls = {"name": celpy.celtypes.StringType}
    >>> env = celpy.Environment(annotations=decls)
    >>> ast = env.compile(cel_source)
    >>> prgm = env.program(ast)

    >>> context = {
    ...     "name": "CEL"
    ... }
    >>> result = prgm.evaluate(context)
    >>> result
    "Hello world! I'm CEL."

The steps include:

1.  Create a :py:class:`celpy.Environment` with annotations for any variables.
    These kinds of type definitions are atypical for Python, but are part of the definition of the CEL language.

2.  Use :py:meth:`celpy.Environment.compile` to create an AST.

3.  Use :py:meth:`celpy.Environment.program` to build a :py:class:`celpy.Runner` object that will do the final evaluation. This includes the environment and the AST.

4.  Use :py:meth:`celpy.Runner.evaluate` to evaluate the program with specific values for the defined variables.

In the Go world, there's a formal type adapter to convert input values to the objects used by CEL.
For numerous types, a default adapter handles this.

In Python, on the other hand, we define the type conversions as features of the Python versions of the CEL types.
This approach fits better with native Python programming.


Function Bindings
=================

There are two function binding examples in
https://github.com/google/cel-go/blob/master/examples/README.md.

There is a complication here that based on the way the Go resolves overloaded functions.
In Go, each overload of a function is described by a ``("name", [args], result)`` data structure.
The key of ``("name", [args], result)`` maps to a specific ``arg_name_arg()`` or ``name_arg()`` overloaded implementation for specific argument types.
This allows for multiple type-specific overload versions of a generic function.

For example, a ``("greet", [StringType, StringType], StringType)`` structure is expected to map to a function ``string_greet_string()`` that has the expected signature.

This is emphatically not how Python generally works.
We follow a more Pythonic approach is to provide a single, generic, function which examines the arguments and decides what to do.
Outside type-checking, Python doesn't depend on overloaded name resolution.

This means a Python function must then sort out type variants and handle argument value coercion on its own.
For most cases, the ``match/case`` statement is helpful for this.
The :py:func:`functools.singledispatch` decorator can also be helpful for this.

The two examples have slightly different approaches to the CEL expression.
These are important in Go, but less important in Python.

Custom function in Go
---------------------------------------

We want to evaluate the CEL expression ``i.greet(you)`` with:

..  parsed-literal::

    i       -> CEL
    you     -> world
    greet   -> "Hello %s! Nice to meet you, I'm %s."

The idea here is the new ``greet()`` behaves like a method of a String.
The actual implementation, however, is not a method; it's a function of two arguments.

First we need to declare two string variables and a ``greet()`` function.
In Go, a ``NewInstanceOverload`` must be used to provide annotations for variables and the function.
Here's the Go implementation:

..  code-block:: go

    decls.NewVar("i", decls.String),
    decls.NewVar("you", decls.String),
    decls.NewFunction("greet",
        decls.NewInstanceOverload("string_greet_string",
            []*exprpb.Type{decls.String, decls.String},
            decls.String))
    ... // Create env and compile

We've omitted the Go details of creating an environment and compiling the CEL expression.
These aren't different from the previous examples.

Separately, a ``greetFunc()`` function must be defined.
In Go, this function is then bound to the ``"string_greet_string"`` overload,
ready for evaluation.
Here's the Go implementation:

..  code-block:: go

    greetFunc := &functions.Overload{
        Operator: "string_greet_string",
        Binary: func(lhs ref.Val, rhs ref.Val) ref.Val {
            return types.String(
                fmt.Sprintf("Hello %s! Nice to meet you, I'm %s.\n", rhs, lhs))
            }}
    prg, err := env.Program(c, cel.Functions(greetFunc))

    out, _, err := prg.Eval(map[string]interface{}{
        "i": "CEL",
        "you": "world",
    })
    fmt.Println(out)
    // Output:Hello world! Nice to meet you, I'm CEL.

What's essential is defining some type information, then defining variables and functions that fit those types.

The Python version has the same outline:

1.  An :py:class:`celpy.Environment` with type annotations for the two variables and the function.

2.  Compile the source.

3.  Define the ``greet()`` function. While the CEL syntax  of ``i.greet(you)`` looks like a method
of the ``i`` variable's class, the function is simply has two positional parameters.

4.  Provide function implementation when creating the final :py:class:`celpy.Runner` instance.

5.  Evaluate the program with specific values for the two variables.

..  code-block:: python

    >>> import celpy
    >>> cel_source = """
    ... i.greet(you)
    ... """

    >>> decls = {
    ...     "i": celpy.celtypes.StringType,
    ...     "you": celpy.celtypes.StringType,
    ...     "greet": celpy.celtypes.FunctionType}
    >>> env = celpy.Environment(annotations=decls)
    >>> ast = env.compile(cel_source)
    >>> def greet(lhs: celpy.celtypes.StringType, rhs: celpy.celtypes.StringType) -> celpy.celtypes.StringType:
    ...     return "Hello {1:s}! Nice to meet you, I'm {0:s}.\\n".format(lhs, rhs)
    >>> prgm = env.program(ast, functions=[greet])
    >>> context = {
    ...     "i": "CEL", "you": "world"
    ... }
    >>> result = prgm.evaluate(context)
    >>> result
    "Hello world! Nice to meet you, I'm CEL.\\n"

The key concept here is to distinguish between three distinct attributes:

1.  Type annotations associated with variables or functions.

2.  The function implementations used to build the :py:class:`celpy.Runner`.
    The method-like syntax of ``i.greet(you)`` is evaluated as ``greet(i, you)``.

3.  The variable values, which provide a context in which the runner evaluates the CEL expression.

This reflects the idea that one CEL expression may be used to process data over and over again.

Define custom global function
-----------------------------

In Go, this is a small, but important different.ce
We want to evaluate the expression ``shake_hands(i,you)``.
This uses a global function syntax instead of method syntax.

While Go has slight differences in how the function is defined, in Python, there is no change.

Here's the Python version:

..  code-block:: python

    >>> import celpy
    >>> cel_source = """
    ... shake_hands(i,you)
    ... """

    >>> decls = {
    ...     "i": celpy.celtypes.StringType,
    ...     "you": celpy.celtypes.StringType,
    ...     "shake_hands": celpy.celtypes.FunctionType}
    >>> env = celpy.Environment(annotations=decls)
    >>> ast = env.compile(cel_source)
    >>> def shake_hands(lhs: celpy.celtypes.StringType, rhs: celpy.celtypes.StringType) -> celpy.celtypes.StringType:
    ...     return f"{lhs} and {rhs} are shaking hands.\\n"
    >>> prgm = env.program(ast, functions=[shake_hands])
    >>> context = {
    ...     "i": "CEL", "you": "world"
    ... }
    >>> result = prgm.evaluate(context)
    >>> result
    'CEL and world are shaking hands.\\n'


The ``shake_hands()`` function is essentially the same as the ``greet()`` function in the previous example.

For more examples of how to use CEL from Go, see
https://github.com/google/cel-go/tree/master/cel/cel_test.go

More Examples from the Go implementation
=========================================

See https://github.com/google/cel-go/blob/master/README.md for five more examples.

..  code-block::

    // Check whether a resource name starts with a group name.
    resource.name.startsWith("/groups/" + auth.claims.group)

    // Determine whether the request is in the permitted time window.
    request.time - resource.age < duration("24h")

    // Check whether all resource names in a list match a given filter.
    auth.claims.email_verified && resources.all(r, r.startsWith(auth.claims.email))

    // Ensure all tweets are less than 140 chars
    tweets.all(t, t.size() <= 140)

    // Test whether the field is a non-default value if proto-based, or defined
    // in the JSON case.
    has(message.field)

Here's the first example, ``resource.name.startsWith("/groups/" + auth.claims.group)``.
The Go code is as follows:

..  code-block:: go

    import(
        "github.com/google/cel-go/cel"
        "github.com/google/cel-go/checker/decls"
    )

    env, err := cel.NewEnv(
        cel.Declarations(
            decls.NewVar("name", decls.String),
            decls.NewVar("group", decls.String)))

    ast, issues := env.Compile(`name.startsWith("/groups/" + group)`)
    if issues != nil && issues.Err() != nil {
        log.Fatalf("type-check error: %s", issues.Err())
    }
    prg, err := env.Program(ast)
    if err != nil {
        log.Fatalf("program construction error: %s", err)
    }

    // The `out` var contains the output of a successful evaluation.
    // The `details' var would contain intermediate evaluation state if enabled as
    // a cel.ProgramOption. This can be useful for visualizing how the `out` value
    // was arrive at.
    out, details, err := prg.Eval(map[string]interface{}{
        "name": "/groups/acme.co/documents/secret-stuff",
        "group": "acme.co"})
    fmt.Println(out) // 'true'

This has a Python implementation which is substantially similar.
Here's the Python code:

..  code-block:: python

    >>> import celpy
    >>> decls = {
    ...     "name": celpy.celtypes.StringType,
    ...     "group": celpy.celtypes.StringType,
    ... }
    >>> env = celpy.Environment(annotations=decls)
    >>> ast = env.compile('name.startsWith("/groups/" + group)')
    >>> prgm = env.program(ast)
    >>> context = {
    ...     "name": "/groups/acme.co/documents/secret-stuff",
    ...     "group": "acme.co",
    ... }
    >>> result = prgm.evaluate(context)
    >>> result
    BoolType(True)

The general outline of compile, create a :py:class:`celpy.Runner`, and use :py:meth:`celpy.Runner.evaluate` to evaluate the CEL expression in a specific context is the central point here.

Exceptions and Errors
======================

Exceptions raised in Python world will (eventually) crash the CEL evaluation.
This gives the author of an extension function the complete traceback to help fix the Python code.
No masking or rewriting of Python exceptions ever occurs in extension functions.

A special :py:exc:`celpy.CELEvalError` exception can be used in an extension function to permit CEL's short-circuit logic processing to check and ignore an exception.
See the https://github.com/google/cel-go/blob/master/README.md#partial-state for more examples of how the short-circuit (partial state) operations work.

An extension function can **return** a :py:exc:`celpy.CELEvalError` object instead of raising it.
This can allow processing to continue in spite of an uncomputable value.

..  code-block:: python

    from celpy import *
    def my_extension(a: Value) -> Value:
        try:
            return celtypes.UintType(64 // a)
        except DivideByZeroError as ex:
            return CELEvalError(f"my_extension({a}) error")

The returned exception object allows short-circuit processing.
For example, the CEL expression ``false && my_extension(0)`` evaluates to ``false``.
If computed, any :exc:`celpy.CELEvalError` objects will be silently ignored because the short-circuit result is known from the presence of a ``false`` value.

On the other hand, the CEL expression ``true && my_extension(0)`` results in the :exc:`celpy.CELEvalError` result from the extension function.
This will eventually be raised as an exception, so the framework using ``celpy`` can track this run-time error.

Cloud Custodian (C7N) Integration
==================================

Custodian Filters can be evaluated by CEL.
The idea is to extend the YAML-based DSL for policy documents to introduce easier-to-read expressions.

As noted in https://github.com/cloud-custodian/cloud-custodian/issues/5759, a filter might look like the
following::

      filters:
        - type: cel
           expr: |
               resource.creationTimestamp < timestamp("2018-08-03T16:00:00-07:00") &&
               resource.deleteProtection == false &&
               ((resource.name.startsWith("projects/project-123/zones/us-east1-b/instances/dev") ||
               (resource.name.startsWith("projects/project-123/zones/us-east1-b/instances/prod"))) &&
               resource.instanceSize == "m1.standard")

This replaces a complex sequence of nested ``-  and:`` and ``-  or:`` sub-documents with a CEL expression.

C7N processioning works by gathering resources, creating an instance of a subclass of the ``Filter`` class, and evaluating an expression like ``take_action = list(filter(filter_instance, resource_list))``.

The C7N filter expression in a given policy document is composed of one or more atomic filter clauses, combined by ``and``, ``or``, and ``not`` operators.
The filter as a whole is handled by the ``__call__()`` methods of subclasses of the ``BooleanGroupFilter`` class.

Central to making this work is making the CEL expression into a function that can be applied to the ``resource`` object.
All CEL versions of a filter will need to have a the following two values in their activations:

:resource:
    A :py:class:`celtypes.MapType` document with the resource details.

:now:
    A :py:class:`celtypes.TimestampType` object with the current time.


Baseline C7N Example
--------------------

The essence of the integration is to provide a resource description to a function defined as a CEL expression, and receive a boolean result.

Here's a base example:

..  code-block:: python

    >>> import celpy
    >>> env = celpy.Environment()
    >>> CEL = """
    ... resource.creationTimestamp < timestamp("2018-08-03T16:00:00-07:00") &&
    ... resource.deleteProtection == false &&
    ... ((resource.name.startsWith(
    ...       "projects/project-123/zones/us-east1-b/instances/dev") ||
    ... (resource.name.startsWith(
    ...       "projects/project-123/zones/us-east1-b/instances/prod"))) &&
    ... resource.instanceSize == "m1.standard")
    ... """
    >>> ast = env.compile(CEL)
    >>> functions = {}
    >>> prgm = env.program(ast, functions)
    >>> activation = {
    ...     "resource":
    ...         celpy.celtypes.MapType({
    ...            "creationTimestamp": celpy.celtypes.TimestampType("2018-07-06T05:04:03Z"),
    ...            "deleteProtection": celpy.celtypes.BoolType(False),
    ...            "name": celpy.celtypes.StringType("projects/project-123/zones/us-east1-b/instances/dev/ec2"),
    ...            "instanceSize": celpy.celtypes.StringType("m1.standard"),
    ...             # MORE WOULD GO HERE
    ...     })
    ... }
    >>> prgm.evaluate(activation)
    BoolType(True)

In this case, the context contained only one variable, ``resource``.
It didn't require a definition of ``now``.

Bulk Filter Example
-------------------

Pragmatically, C7N works via code somewhat like the following:

..  code-block::

    resources = [provider.describe(r) for r in provider.list(resource_type)]
    map(action, list(filter(cel_program, resources)))

An action is applied to those resources that pass some filter test.
Often, the action disables a resource to prevent data compromise.
The filter looks for items not compliant with policies so they can be deleted or disabled.

The ``cel_program`` in the above example is an executable CEL program wrapped into a C7N ``Filter`` subclass.

..  code-block::

    >>> import celpy
    >>> import datetime
    >>> cel_functions = {}

    >>> class Filter:
    ...     def __call__(self, resource):
    ...         raise NotImplementedError
    ...
    >>> class CelFilter(Filter):
    ...     env = celpy.Environment()
    ...     def __init__(self, object):
    ...         assert object["type"] == "cel", "Can't create CelFilter without filter: - type: \"cel\""
    ...         assert "expr" in object, "Can't create CelFilter without filter: - expr: \"CEL expression\""
    ...         ast = self.env.compile(object["expr"])
    ...         self.prgm = self.env.program(ast, cel_functions)
    ...     def __call__(self, resource):
    ...         now = datetime.datetime.now(tz=datetime.timezone.utc)
    ...         activation = {"resource": celpy.json_to_cel(resource), "now": celpy.celtypes.TimestampType(now)}
    ...         return bool(self.prgm.evaluate(activation))

    >>> tag_policy = {
    ...     "filter": {
    ...         "type": "cel",
    ...         "expr": "! has(resource.tags.owner) || size(resource.tags.owner) == 0"
    ...     }
    ... }
    >>> resources = [
    ...     {"name": "good", "tags": {"owner": "me"}},
    ...     {"name": "bad1", "tags": {"not-owner": "oops"}},
    ...     {"name": "bad2", "tags": {"owner": None}},
    ... ]
    >>> tag_policy_filter = CelFilter(tag_policy["filter"])
    >>> actionable = list(filter(tag_policy_filter, resources))
    >>> actionable
    [{'name': 'bad1', 'tags': {'not-owner': 'oops'}}, {'name': 'bad2', 'tags': {'owner': None}}]

For each resource, the ``tag_policy_filter`` object applied an internal ``self.prgm`` to the resource.
The internal ``self.prgm`` was built from the policy expression, stated in CEL.

C7N Filter and Resource Types
-------------------------------

The :py:mod:`celpy.c7nlib` module provides filter subclasses that include CEL processing.
There are two kinds of C7N filters in use.

1.  The :py:mod:`c7n.filters` package defines about 23 generic filter classes.
    These apply to a ``resource`` object.
    Additionally, there's a library of generic functions used for evaluation.
    Generally, the resource definition classes create values in a JSON document.
    These values reflect the state of the resource and any closely-related resources.

2.  The :py:mod:`c7n.resources` package defines a number of additional resource-specific filters.
    These classes can also provide additional resource-specific processing.

The atomic filter clauses within a policy document have two general forms:

-   Those with "op". These expose a resource attribute value,
    a filter comparison value, and an operator.
    For example, ``resource.creationTimestamp < timestamp("2018-08-03T16:00:00-07:00")``.

-   Those without "op". These tests are based on a boolean function embedded in the C7N resource definition class.
    For example, ``! resource.deleteProtection`` could rely on a attribute with a complex
    value computed from one or more resource attribute values.

The breakdown of ``filter`` rules in the C7N policy schema has the following counts.

..  csv-table::
    :header: category, count, notes

    "('Common', 'Op')",21,"Used for more than one resource type, exposes resource details to CEL"
    "('Common', 'No-Op')",15,"Used for more than one resource type, does not expose resource details"
    "('Singleton', 'Op')",27,"Used for exactly one resource type, exposes resource details to CEL"
    "('Singleton', 'No-Op')",47,"Used for exactly one resource type, does not expose resource details"

(This is based on cloud-custodian-0.8.40.0, newer versions may have slighyly different numbers.)

External API
=============

The key external components are the following:

-   :py:class:`celpy.__init__.Environment`

    This has two methods of interest:

    -   :py:meth:`celpy.__init__.Environment.compile`

    -   :py:meth:`celpy.__init__.Environment.program`

-   :py:class:`celpy.__init__.Runner`

    This has one method of interest:

    -   :py:meth:`celpy.__init__.Runner.evaluate`.

-   :py:func:`celpy.adapter.json_to_cel`

    This is used to convert native Python JSON documents to the appropriate CEL types.

..  uml::

    @startuml
        class YourApp

        package celpy {
            class Environment {
                compile()
                program()
            }
            abstract class Runner {
                evaluate(context)
            }
            Environment -> Runner

            class CompiledRunner
            class InterpretedRunner

            Runner <|-- CompiledRunner
            Runner <|-- InterpretedRunner
        }

        YourApp *--> Environment : "Creates"

        YourApp *--> Runner : "Evaluates"

    @enduml
