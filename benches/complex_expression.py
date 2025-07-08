"""
https://github.com/cloud-custodian/cel-python/issues/68

Performance of the given expression is perfectly awful.

What can be done to make it better?
"""
import timeit
import cProfile
import pstats
from textwrap import dedent

import celpy
import celpy.celtypes

CEL_EXPRESSION_ORIGINAL = """
(
    (
        !has(class_a.property_a) ? 
            false : ("Linux" == class_a.property_a)
    ) && 
    (
        (
            !has(class_b.property_b) ? 
                false : class_b.property_b.contains("os:/o:centos:centos:")
        ) || 
        (
            !has(class_b.property_b) ?
                false : class_b.property_b.contains("x-os:/o:centos:centos:")
        ) || 
        (
            !has(class_b.property_b) ?
                false : class_b.property_b.contains("os:/a:centos:centos:")
        ) || 
        (
            !has(class_b.property_b) ?
                false : class_b.property_b.contains("x-os:/a:centos:centos:")
        ) || 
        (
            !has(class_b.property_b) ? 
                false : class_b.property_b.contains("p-os:/a:centos:centos:")
        )
    )
) ? 
optional.of("Linux Team") : 
(
    (
        (
            !has(class_a.property_a) ?
                false : ("Linux" == class_a.property_a)
        ) && 
        (
            (
                !has(class_b.property_b) ?
                    false : class_b.property_b.contains("os:/o:debian:debian_linux:")
            ) || 
            (
                !has(class_b.property_b) ?
                    false : class_b.property_b.contains("x-os:/o:debian:debian_linux:")
            ) || 
            (
                !has(class_b.property_b) ?
                    false : class_b.property_b.contains("os:/a:debian:debian:")
            ) || 
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("x-os:/a:debian:debian:")
            ) || 
            (
                !has(class_b.property_b) ?
                    false : class_b.property_b.contains("p-os:/a:debian:debian_linux:")
            )
        )
    ) ?
optional.of("Linux Team") : 
(
    (
        (
            !has(class_a.property_a) ?
                false : ("Linux" == class_a.property_a)
        ) && 
        (
            (
                !has(class_b.property_b) ?
                    false : class_b.property_b.contains("os:/o:fedoraproject:fedora:")
            ) || 
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("x-os:/o:fedoraproject:fedora:")
            ) || 
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("os:/a:fedoraproject:fedora:")
            ) || 
            (
                !has(class_b.property_b) ?
                    false : class_b.property_b.contains("x-os:/a:fedoraproject:fedora:")
            ) || 
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("p-os:/a:fedoraproject:fedora:")
            )
        )
    ) ? 
optional.of("Linux Team") : 
(
    (
        (
            !has(class_a.property_a) ? 
                false : ("Linux" == class_a.property_a)
        ) && 
        (
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("os:/o:oracle:linux:")
            ) || 
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("x-os:/o:oracle:linux:")
            ) || 
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("os:/a:oracle:linux:")
            ) || 
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("x-os:/a:oracle:linux:")
            ) || 
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("p-os:/a:oracle:linux:")
            )
        )
    ) ? 
optional.of("Linux Team") : 
(
    (
        (
            !has(class_a.property_a) ? 
                false : ("Linux" == class_a.property_a)
        ) && 
        (
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("os:/o:redhat:enterprise_linux:")
        ) || 
        (
            !has(class_b.property_b) ? 
                false : class_b.property_b.contains("x-os:/o:redhat:enterprise_linux:")
        ) || 
        (
            !has(class_b.property_b) ? 
                false : class_b.property_b.contains("os:/a:redhat:enterprise_linux:")
        ) || 
        (
            !has(class_b.property_b) ? 
                false : class_b.property_b.contains("x-os:/a:redhat:enterprise_linux:")
        ) || 
        (
            !has(class_b.property_b) ? 
                false : class_b.property_b.contains("p-os:/a:redhat:enterprise_linux:")
        )
    )
) ? 
optional.of("Linux Team") : 
(
    (
        (
            !has(class_a.property_a) ? 
                false : ("Linux" == class_a.property_a)
        ) && (
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("os:/o:novell:suse_linux:")
            ) || 
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("x-os:/o:novell:suse_linux:")
            ) || 
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("os:/a:novell:suse_linux:")
            ) || 
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("x-os:/a:novell:suse_linux:")
            ) || 
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("p-os:/a:novell:suse_linux:")
            )
        )
    ) ? 
optional.of("Linux Team") : 
(
    (
        (
            !has(class_a.property_a) ? 
                false : ("Linux" == class_a.property_a)
        ) && 
        (
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("os:/o:canonical:ubuntu_linux:")
            ) || 
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("x-os:/o:canonical:ubuntu_linux:")
            ) || 
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("os:/a:canonical:ubuntu_linux:")
            ) || 
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("x-os:/a:canonical:ubuntu_linux:")
            ) || 
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("p-os:/a:canonical:ubuntu_linux:")
            )
        )
    ) ? 
optional.of("Linux Team") : 
(
    (
        (
            !has(class_a.property_a) ? 
                false : ("Linux" == class_a.property_a)
        ) && 
        (
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("os:/h:")
            ) || 
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("x-os:/h:")
            )
        )
    ) ? 
optional.of("Linux Team") : 
(
    (
        (
            !has(class_a.property_a) ? 
                false : ("Windows Server" == class_a.property_a)
        ) && 
        (
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("os:/o:microsoft:")
            ) || 
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("x-os:/o:microsoft:")
            ) || 
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("os:/a:microsoft:")
            ) || 
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("x-os:/a:microsoft:")
            )
        )
    ) ? 
optional.of("Windows Team") : 
(
    (
        (
            !has(class_a.property_a) ? 
                false : ("Windows Server" == class_a.property_a)
        ) && 
        (
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("os:/h:")
            ) || 
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("x-os:/h:")
            )
        )
    ) ? 
optional.of("Windows Team") : 
(
    (
        (
            !has(class_a.property_a) ? 
                false : ("Linux" == class_a.property_a)
        ) || 
        (
            !has(class_a.property_a) ?   
                false : ("Windows Server" == class_a.property_a)
        )
    ) ? 
optional.of("Unassigned") : 
(
    (
        (
            !has(class_a.property_a) ? 
                false : ("Windows Workstation" == class_a.property_a)
        ) && 
        (
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("os:/o:microsoft:")
            ) || 
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("x-os:/o:microsoft:")
            ) || 
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("os:/a:microsoft:")
            ) || 
            (
                !has(class_b.property_b) ? 
                    false : class_b.property_b.contains("x-os:/a:microsoft:")
            )
        )
    ) ? 
optional.of("Solutions Team") : 
(
    (
        !has(class_a.property_a) ? 
            false : ("Windows Workstation" == class_a.property_a)
    ) ? 
optional.of("End User") : optional.of("Unknown")))))))))))))
"""


CEL_EXPRESSION_SHORT = """
    "bla bla"
"""

CEL_EXPRESSION_MEDIUM = """
    (!has(class_b.integration_info.type) ?
                false:("some value" == class_b.integration_info.type)) ?
                optional.of("some value") : optional.of("some other value")
"""

CEL_EXPRESSION_ORIGINAL_NO_OPTIONAL = """
((!has(class_a.property_a) ? false : ("Linux" == class_a.property_a)) && ((!has(class_b.property_b) ? false : class_b.property_b.contains("os:/o:centos:centos:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("x-os:/o:centos:centos:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("os:/a:centos:centos:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("x-os:/a:centos:centos:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("p-os:/a:centos:centos:")))) ? "Linux Team" : (((!has(class_a.property_a) ? false : ("Linux" == class_a.property_a)) && ((!has(class_b.property_b) ? false : class_b.property_b.contains("os:/o:debian:debian_linux:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("x-os:/o:debian:debian_linux:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("os:/a:debian:debian:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("x-os:/a:debian:debian:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("p-os:/a:debian:debian_linux:")))) ? "Linux Team" : (((!has(class_a.property_a) ? false : ("Linux" == class_a.property_a)) && ((!has(class_b.property_b) ? false : class_b.property_b.contains("os:/o:fedoraproject:fedora:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("x-os:/o:fedoraproject:fedora:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("os:/a:fedoraproject:fedora:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("x-os:/a:fedoraproject:fedora:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("p-os:/a:fedoraproject:fedora:")))) ? "Linux Team" : (((!has(class_a.property_a) ? false : ("Linux" == class_a.property_a)) && ((!has(class_b.property_b) ? false : class_b.property_b.contains("os:/o:oracle:linux:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("x-os:/o:oracle:linux:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("os:/a:oracle:linux:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("x-os:/a:oracle:linux:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("p-os:/a:oracle:linux:")))) ? "Linux Team" : (((!has(class_a.property_a) ? false : ("Linux" == class_a.property_a)) && ((!has(class_b.property_b) ? false : class_b.property_b.contains("os:/o:redhat:enterprise_linux:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("x-os:/o:redhat:enterprise_linux:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("os:/a:redhat:enterprise_linux:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("x-os:/a:redhat:enterprise_linux:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("p-os:/a:redhat:enterprise_linux:")))) ? "Linux Team" : (((!has(class_a.property_a) ? false : ("Linux" == class_a.property_a)) && ((!has(class_b.property_b) ? false : class_b.property_b.contains("os:/o:novell:suse_linux:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("x-os:/o:novell:suse_linux:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("os:/a:novell:suse_linux:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("x-os:/a:novell:suse_linux:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("p-os:/a:novell:suse_linux:")))) ? "Linux Team" : (((!has(class_a.property_a) ? false : ("Linux" == class_a.property_a)) && ((!has(class_b.property_b) ? false : class_b.property_b.contains("os:/o:canonical:ubuntu_linux:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("x-os:/o:canonical:ubuntu_linux:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("os:/a:canonical:ubuntu_linux:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("x-os:/a:canonical:ubuntu_linux:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("p-os:/a:canonical:ubuntu_linux:")))) ? "Linux Team" : (((!has(class_a.property_a) ? false : ("Linux" == class_a.property_a)) && ((!has(class_b.property_b) ? false : class_b.property_b.contains("os:/h:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("x-os:/h:")))) ? "Linux Team" : (((!has(class_a.property_a) ? false : ("Windows Server" == class_a.property_a)) && ((!has(class_b.property_b) ? false : class_b.property_b.contains("os:/o:microsoft:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("x-os:/o:microsoft:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("os:/a:microsoft:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("x-os:/a:microsoft:")))) ? "Windows Team" : (((!has(class_a.property_a) ? false : ("Windows Server" == class_a.property_a)) && ((!has(class_b.property_b) ? false : class_b.property_b.contains("os:/h:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("x-os:/h:")))) ? "Windows Team" : (((!has(class_a.property_a) ? false : ("Linux" == class_a.property_a)) || (!has(class_a.property_a) ? false : ("Windows Server" == class_a.property_a))) ? "Unassigned" : (((!has(class_a.property_a) ? false : ("Windows Workstation" == class_a.property_a)) && ((!has(class_b.property_b) ? false : class_b.property_b.contains("os:/o:microsoft:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("x-os:/o:microsoft:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("os:/a:microsoft:")) || (!has(class_b.property_b) ? false : class_b.property_b.contains("x-os:/a:microsoft:")))) ? "Solutions Team" : ((!has(class_a.property_a) ? false : ("Windows Workstation" == class_a.property_a)) ? "End User" : "unknown"))))))))))))
"""


functions = {
    "of": lambda optional, value: value,
    "none": lambda optional, : None
}

def simple_performance(runner_class: type[celpy.Runner] | None = None) -> None:
    env = celpy.Environment(runner_class=runner_class)

    number = 100
    compile = timeit.timeit(
        stmt=dedent("""\
            env.compile(CEL_EXPRESSION_ORIGINAL_NO_OPTIONAL)
        """),
        globals={
            'env': env,
            'CEL_EXPRESSION_ORIGINAL_NO_OPTIONAL': CEL_EXPRESSION_ORIGINAL_NO_OPTIONAL
        },
        number=number
    )
    print(f"Compile:  {1_000 * compile / number:9.4f} ms")

    ast = env.compile(CEL_EXPRESSION_ORIGINAL_NO_OPTIONAL)

    number = 1_000
    prepare = timeit.timeit(
        stmt=dedent("""\
            env.program(ast,functions=functions)
        """),
        globals={
            'env': env,
            'ast': ast,
            'functions': functions
        },
        number=number
    )
    print(f"Prepare:  {1_000 * prepare / number:9.4f} ms")

    program = env.program(ast, functions=functions)

    number = 1_000
    convert = timeit.timeit(
        stmt=dedent("""
            {
                "class_a": celpy.json_to_cel({"property_a": "something"}),
                "class_b": celpy.json_to_cel(
                    {"title": "something else", "property_b": "some var",
                     "integration_info": {"type": "GitHub"}}),
                "optional": celpy.json_to_cel({})
            }
        """),
        globals={'celpy': celpy},
        number=number
    )
    print(f"Convert:  {1_000 * convert / number:9.4f} ms")

    cel_context = {
        "class_a": celpy.json_to_cel({"property_a": "something"}),
        "class_b": celpy.json_to_cel(
            {"title": "something else", "property_b": "some var",
             "integration_info": {"type": "GitHub"}}),
        "optional": celpy.json_to_cel({})
    }

    number = 100
    evaluation = timeit.timeit(
        stmt=dedent("""
            program.evaluate(cel_context)
        """),
        globals = {
            'program': program,
            'cel_context': cel_context
        },
        number=number
    )
    print(f"Evaluate: {1_000 * evaluation / number:9.4f} ms")

    print()


def process(program: celpy.CompiledRunner, number: int = 100):
    """A processing loop that prepares data and evaluates the CEL program."""
    for i in range(number):
        cel_context = {
                        "class_a": celpy.json_to_cel({"property_a":"something"}),
                        "class_b": celpy.json_to_cel({"title":"something else","property_b":"some var","integration_info":{"type":"GitHub"}}),
                        "optional": celpy.json_to_cel({})
                    }
        result = program.evaluate(cel_context)
    assert result == "unknown"

def detailed_profile():
    env = celpy.Environment()
    ast = env.compile(CEL_EXPRESSION_ORIGINAL_NO_OPTIONAL)
    program = env.program(ast, functions=functions)

    pr = cProfile.Profile()
    pr.enable()
    process(program)
    pr.disable()

    ps = pstats.Stats(pr).sort_stats(pstats.SortKey.TIME)
    ps.print_stats()

def main():
    print("# Performance")
    print()
    print("## Interpreter")
    print()
    simple_performance(celpy.InterpretedRunner)
    print()
    print("## Transpiler")
    print()
    simple_performance(celpy.CompiledRunner)
    print()
    print("# Profile")
    print()
    detailed_profile()

if __name__ == "__main__":
    main()
