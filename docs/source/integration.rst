..  comment
    # Copyright 2020 The Cloud Custodian Authors.
    # SPDX-License-Identifier: Apache-2.0

########################
Application Integration
########################

We'll look at the essential base case for integration:
evaluate a function given some variable bindings.

Then we'll look at providing custom function bindings to extend
the environment.

We'll also look at additional examples from the Go implementation.
This will lead us to providing custom type providers
and custom type adapters.

There are a few exception and error-handling cases that are helpful
for writing CEL that tolerates certain kinds of data problems.

Finally, we'll look at how CEL can be integrated into Cloud Custodian.

The Essentials
==============

Here are two examples of variable bindings

README
------

Here's the example taken from the README.

The baseline implementation works like this::

    >>> import celpy
    >>> cel_source = """
    ... account.balance >= transaction.withdrawal
    ... || (account.overdraftProtection
    ... && account.overdraftLimit >= transaction.withdrawal - account.balance)
    ... """

    >>> env = celpy.Environment()
    >>> ast = env.compile(cel_source)
    >>> prgm = env.program(ast)

    >>> activation = {
    ...     "account": celpy.json_to_cel({"balance": 500, "overdraftProtection": False}),
    ...     "transaction": celpy.json_to_cel({"withdrawal": 600})
    ... }
    >>> result = prgm.evaluate(activation)
    >>> result
    BoolType(False)

The :py:class:`celpy.Environment` can include type adapters and type providers. It's not clear
how these should be implemented in Python or if they're even necessary.

The compile step creates a syntax tree, which is used to create a final program to evaluate.
Currently, there's a two-step process because we might want to optimize or transform the AST prior
to evaluation.

The activation provides specific variable values used to evaluate the program.

To an extent, the Python classes are loosely based on the object model in https://github.com/google/cel-go.
We don't need all the Go formalisms, however, and rely on Pythonic variants.

Simple example using builtin operators
---------------------------------------

Here's an example taken from
https://github.com/google/cel-go/blob/master/examples/README.md

Evaluate expression ``"Hello world! I'm " + name + "."`` with ``CEL`` passed as
the ``name`` variable.

..  code:: go

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

Here's the Python version::

    >>> import celpy
    >>> cel_source = """
    ... "Hello world! I'm " + name + "."
    ... """

    >>> decls = {"name": celpy.celtypes.StringType}
    >>> env = celpy.Environment(annotations=decls)
    >>> ast = env.compile(cel_source)
    >>> prgm = env.program(ast)

    >>> activation = {
    ...     "name": "CEL"
    ... }
    >>> result = prgm.evaluate(activation)
    >>> result
    "Hello world! I'm CEL."

There's a big open concern here: there's no formal type adapter implementation.
Nothing converts from the input value in the activation to the proper underlying
type. This relies on Python's built-in type conversions.

..  todo:: Handle type adapters properly.

Function Bindings
=================

Here are two more examples of binding, taken from
https://github.com/google/cel-go/blob/master/examples/README.md

Note the complication here comes from the way the Go implementation resolves overloaded functions.
Each CEL overload of a function is described by a ``("name", [args], result)`` structure.
This allows for multiple type-specific overload versions of a generic function.

The key of ``("name", [args], result)`` maps to a specific ``arg_name_arg()`` or ``name_arg()``
overloaded implementation for specific argument types.

For example, ``("greet", [StringType, StringType], StringType)`` maps to ``string_greet_string()``.

This is emphatically not how Python generally works. A more Pythonic approach is to provide
a single, generic, function which examines the arguments and decides what to do. Python doesn't
generally do overloaded name resolution.

There are two choices:

1.  Build a mapping from ``("name", [args], result)`` to a specific overloaded implementation.
    This pulls argument and result type coercion outside the Python function.
    It matches the Go implementation, but can be confusing for Python implementers.
    This requires exposing a great deal of machinery already available in a Python function
    definition.

2.  Ignore the complex type exposture techniques that Go requiees and dispatch to a Python function.
    The Python function will sort out type variants and handle argument value coercion on its own.
    This simplifies implementation down to name resolution.
    Indeed, the type mapping rules can introspect Python's type annotations on the function
    definition.

We follow the 2nd alternative. The Python function binding relies -- exclusively -- on introspection
of the function provided.

Custom function on string type
------------------------------

Evaluate expression ``i.greet(you)`` with:

..  parsed-literal::

    i       -> CEL
    you     -> world
    greet   -> "Hello %s! Nice to meet you, I'm %s."


First we need to declare two string variables and `greet` function.
`NewInstanceOverload` must be used if we want to declare function which will
operate on a type. First element of slice passed as `argTypes` into
`NewInstanceOverload` is declaration of instance type. Next elements are
parameters of function.

..  code:: go

    decls.NewVar("i", decls.String),
    decls.NewVar("you", decls.String),
    decls.NewFunction("greet",
        decls.NewInstanceOverload("string_greet_string",
            []*exprpb.Type{decls.String, decls.String},
            decls.String))
    ... // Create env and compile


Let's implement `greet` function and pass it to `program`. We will be using
`Binary`, because `greet` function uses 2 parameters (1st instance, 2nd
function parameter).

..  code:: go

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

Here's the Python version::

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
    >>> activation = {
    ...     "i": "CEL", "you": "world"
    ... }
    >>> result = prgm.evaluate(activation)
    >>> result
    "Hello world! Nice to meet you, I'm CEL.\\n"

Define custom global function
-----------------------------

Evaluate expression ``shake_hands(i,you)`` with:

..  parsed-literal::

    i           -> CEL
    you         -> world
    shake_hands -> "%s and %s are shaking hands."


In order to declare global function we need to use `NewOverload`:

..  code:: go

    decls.NewVar("i", decls.String),
    decls.NewVar("you", decls.String),
    decls.NewFunction("shake_hands",
        decls.NewOverload("shake_hands_string_string",
            []*exprpb.Type{decls.String, decls.String},
            decls.String))
    ... // Create env and compile.

    shakeFunc := &functions.Overload{
        Operator: "shake_hands_string_string",
        Binary: func(lhs ref.Val, rhs ref.Val) ref.Val {
            return types.String(
                fmt.Sprintf("%s and %s are shaking hands.\n", lhs, rhs))
            }}
    prg, err := env.Program(c, cel.Functions(shakeFunc))

    out, _, err := prg.Eval(map[string]interface{}{
        "i": "CEL",
        "you": "world",
    })
    fmt.Println(out)
    // Output:CEL and world are shaking hands.

Here's the Python version::

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
    >>> activation = {
    ...     "i": "CEL", "you": "world"
    ... }
    >>> result = prgm.evaluate(activation)
    >>> result
    'CEL and world are shaking hands.\\n'



For more examples of how to use CEL, see
https://github.com/google/cel-go/tree/master/cel/cel_test.go

Examples from Go implementation
================================

See https://github.com/google/cel-go/blob/master/README.md

..  code::

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

Following one of the more complete examples through the README

..  code:: go

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

This has the following Python implementation::

    >>> import celpy
    >>> decls = {
    ...     "name": celpy.celtypes.StringType,
    ...     "group": celpy.celtypes.StringType,
    ... }
    >>> env = celpy.Environment(annotations=decls)
    >>> ast = env.compile('name.startsWith("/groups/" + group)')
    >>> prgm = env.program(ast)
    >>> activation = {
    ...     "name": "/groups/acme.co/documents/secret-stuff",
    ...     "group": "acme.co",
    ... }
    >>> result = prgm.evaluate(activation)
    >>> result
    BoolType(True)

Exceptions and Errors
======================

Exceptions raised in Python world will (eventually) crash the CEL evluation.
This gives the author of an extension function the complete traceback to help
fix the Python code.
No masking or rewriting of Python exceptions ever occurs in extension functions.

A special :exc:`celpy.EvalError` exception can be used in an extension function
to permit CEL's short-circuit logic processing to silence this exception.  See the
https://github.com/google/cel-go/blob/master/README.md#partial-state for more examples
of how the short-circuit (partial state) operations work.

An extension function must **return** a :exc:`celpy.EvalError` object
to allow processing to continue in spite of an uncomputable value.

::

    from celpy import *
    def my_extension(a: Value) -> Value:
        try:
            return celtypes.UintType(64 // a)
        except DivideByZeroError as ex:
            return EvalError(f"my_extnsion({a}) error")

The returned exception object allows short-circuit processing. For example,

::

    false && my_extension(0)

This evaluates to ``false``.  If computed, any :exc:`celpy.EvalError` object will be silently ignored.

On the other hand,

::

    true && my_extension(0)

This will result in a visible :exc:`celpy.EvalError` result from the extension function.
This will eventually be raised as an exception, so the framework using ``celpy`` can track this run-time error.

Cloud Custodian
===============

Custodian Filters can be evaluated by CEL.

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

C7N processes resources by gathering resources, creating an instance of a subclass of the ``Filter``
class, and evaluating an expression like ``take_action = list(filter(filter_instance, resource_list))``.

The C7N filter expression in a given policy document is componsed of one or more atomic filter clauses,
combined by ``and``, ``or``, and ``not`` operators.
The filter as a whole is handled by the ``__call__()`` methods of subclasses of the ``BooleanGroupFilter`` class.

Central to making this work is making the CEL expression into a function that can be applied to the ``resource`` object.
It appears that all CEL operations will need to have a number of values in their activations:

:resource:
    A :py:class:`celtypes.MapType` document with the resource details.

:now:
    A :py:class:`celtypes.TimestampType` object with the current time.

Additional "global" objects may also be helpful.

Baseline C7N Example
--------------------

The essence of the integration is to provide a resource to a function and receive a boolean result.

Here's a base example::

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

Bulk Filter Example
-------------------

Pragmatically, C7N works via code somewhat like the following:

::

    resources = [provider.describe(r) for r in provider.list(resource_type)]
    map(action, list(filter(cel_program, resources)))

An action is applied to those resources that pass some filter test. The filter looks for items not compliant
with policies.

The ``cel_program`` in the above example is an executable CEL program wrapped into a C7N ``Filter`` subclass.

::

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
    ...         now = datetime.datetime.utcnow()
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


C7N Filter and Resource Types
-------------------------------

There are several parts to handling the various kinds of C7N filters in use.

1.  The :py:mod:`c7n.filters` package defines about 23 generic filter classes, all of which need to
    provide the ``resource`` object in the activation, and possibly provide a library of generic
    CEL functions used for evaluation.
    The general cases are of this is handled by the resource definition classes creating  values in a JSON document.
    These values reflect the state of the resource and any closely-related resources.

2.  The :py:mod:`c7n.resources` package defines a number of additional resource-specific filters.
    All of these, similarly, need to provide CEL values as part of the resource object.
    These classes can also provide additional resource-specific CEL functions used for evaluation.

The atomic filter clauses have two general forms:

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
