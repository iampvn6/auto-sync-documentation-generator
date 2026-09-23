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


def test_analyzer_extracts_decorators():
    module = analyze_python_file("examples/sample_app/service.py")

    functions = {function.name: function for function in module.functions}

    assert "create_user" in functions
    assert functions["create_user"].decorators == ["require_auth"]

    assert len(module.classes) == 1
    assert module.classes[0].name == "UserService"

    method = module.classes[0].methods[0]
    assert method.name == "get_user"
