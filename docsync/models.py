from pydantic import BaseModel, Field


class FunctionInfo(BaseModel):
    name: str
    signature: str
    docstring: str | None = None
    line_number: int
    decorators: list[str] = Field(default_factory=list)


class ClassInfo(BaseModel):
    name: str
    docstring: str | None = None
    line_number: int
    methods: list[FunctionInfo] = Field(default_factory=list)
    decorators: list[str] = Field(default_factory=list)


class ModuleInfo(BaseModel):
    name: str
    file_path: str
    functions: list[FunctionInfo]
    classes: list[ClassInfo] = Field(default_factory=list)
