from pydantic import BaseModel


class FunctionInfo(BaseModel):
    name: str
    signature: str
    docstring: str | None = None
    line_number: int


class ModuleInfo(BaseModel):
    name: str
    file_path: str
    functions: list[FunctionInfo]