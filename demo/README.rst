#########################
CEL Demo
#########################

To build CEL filters, it helps to have some kind of development
environment. While CEL can be run from the command line, this
is kind of awkward for developing (and debugging) a filter.

It's better to have an environment where you can look at the AWS
Describe outputs, and the Filter expressions, and confirm the
logic is correct.

We'll put this together using Jupyter Lab. It lets us run
CEL expressions and other analytical tools to be sure we're
properly filtering cloud resource descriptions.

If necessary, install Conda. This is a helpful way to install
Python components and build virtual environments.
For more information see https://docs.conda.io/en/latest/index.html

(Much of this can be done with PIP, also.)

Create and activate a Conda virtual environment, we've used the name "cel"::

    conda create -n cel python=3.8
    conda activate cel

Install Jupyter Lab::

    conda install jupyterlab


Start a lab server::

    PYTHONPATH=$(pwd)/src jupyter lab

The ``$(pwd)`` is essential to make sure Jupyter Lab
can see the ``cel-python`` packages.

When the browser launches, you can click into the `demo`_ directory
and examine the notebooks. We'll look at this from a Cloud Custodian (C7N) perspective.

-   `demo/CEL_Implementation.ipynb`_ provides some details on how the CEL Implementation works.
    This isn't essential, but it can be helpful background.

-   `demo/CEL_Development.ipynb`_ shows how to use Jupyter Lab as an IDE to build (and test) CEL filters.

-   `demo/C7N_Rewrite.ipynb`_ shows how to rewrite Cloud Custodian (C7N) filters into CEL.

-   `demo/complex_policy.ipynb`_ shows a complex policy and how we can build -- and debug -- the policy
    filter expression.

These should help you build an understanding of how to develop complex filters.
