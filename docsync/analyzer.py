import ast
from pathlib import Path

from docsync.models import ClassInfo, FunctionInfo, ModuleInfo


def annotation_to_string(annotation: ast.expr | None) -> str:
    if annotation is None:
        return ""

    return ast.unparse(annotation)


def decorator_names(
    node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
) -> list[str]:
    """Return decorator expressions as strings, e.g. ['require_auth', 'lru_cache(maxsize=128)']."""
    return [
        decorator.id if isinstance(decorator, ast.Name) else ast.unparse(decorator)
        for decorator in node.decorator_list
    ]


def build_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    parameters = []

    positional_arguments = [*node.args.posonlyargs, *node.args.args]
    missing_defaults = len(positional_arguments) - len(node.args.defaults)
    positional_defaults = [None] * missing_defaults + list(node.args.defaults)

    for index, argument in enumerate(positional_arguments):
        parameter = argument.arg
        annotation = annotation_to_string(argument.annotation)

        if annotation:
            parameter = f"{parameter}: {annotation}"

        default_value = positional_defaults[index]

        if default_value is not None:
            parameter += f" = {ast.unparse(default_value)}"

        parameters.append(parameter)

        if node.args.posonlyargs and index == len(node.args.posonlyargs) - 1:
            parameters.append("/")

    if node.args.vararg:
        parameter = f"*{node.args.vararg.arg}"
        annotation = annotation_to_string(node.args.vararg.annotation)

        if annotation:
            parameter += f": {annotation}"

        parameters.append(parameter)

    elif node.args.kwonlyargs:
        parameters.append("*")

    for argument, default_value in zip(
        node.args.kwonlyargs,
        node.args.kw_defaults,
        strict=True,
    ):
        parameter = argument.arg
        annotation = annotation_to_string(argument.annotation)

        if annotation:
            parameter = f"{parameter}: {annotation}"

        if default_value is not None:
            parameter += f" = {ast.unparse(default_value)}"

        parameters.append(parameter)

    if node.args.kwarg:
        parameter = f"**{node.args.kwarg.arg}"
        annotation = annotation_to_string(node.args.kwarg.annotation)

        if annotation:
            parameter += f": {annotation}"

        parameters.append(parameter)

    signature = f"{node.name}({', '.join(parameters)})"
    return_annotation = annotation_to_string(node.returns)

    if return_annotation:
        signature += f" -> {return_annotation}"

    return signature


def analyze_python_file(file_path: str | Path) -> ModuleInfo:
    path = Path(file_path)
    tree = ast.parse(path.read_text(encoding="utf-8"))

    functions = []
    classes = []

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("_"):
                continue

            functions.append(
                FunctionInfo(
                    name=node.name,
                    signature=build_signature(node),
                    docstring=ast.get_docstring(node),
                    line_number=node.lineno,
                    decorators=decorator_names(node),
                )
            )

        elif isinstance(node, ast.ClassDef):
            if node.name.startswith("_"):
                continue

            methods = []

            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if item.name.startswith("_"):
                        continue

                    methods.append(
                        FunctionInfo(
                            name=item.name,
                            signature=build_signature(item),
                            docstring=ast.get_docstring(item),
                            line_number=item.lineno,
                            decorators=decorator_names(item),
                        )
                    )

            classes.append(
                ClassInfo(
                    name=node.name,
                    docstring=ast.get_docstring(node),
                    line_number=node.lineno,
                    methods=methods,
                    decorators=decorator_names(node),
                )
            )
    return ModuleInfo(
        name=path.stem,
        file_path=str(path),
        functions=functions,
        classes=classes,
    )
