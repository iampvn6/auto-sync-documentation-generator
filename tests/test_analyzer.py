from docsync.analyzer import analyze_python_file


def test_analyze_python_file():
    module = analyze_python_file("examples/sample_app/calculator.py")

    assert module.name == "calculator"
    assert len(module.functions) == 2

    add_function = module.functions[0]

    assert add_function.name == "add"
    assert (
        add_function.signature
        == "add(first_number: int, second_number: int, tax: int = 0) -> int"
    )
    assert add_function.docstring == "Return the sum of two numbers and optional tax."


def test_analyzer_includes_default_values():
    module = analyze_python_file("examples/sample_app/calculator.py")

    add_function = module.functions[0]

    assert (
        add_function.signature
        == "add(first_number: int, second_number: int, tax: int = 0) -> int"
    )
