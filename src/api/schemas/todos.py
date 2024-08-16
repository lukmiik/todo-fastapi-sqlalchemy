from pydantic import BaseModel


class TodosCreateIn(BaseModel):
    """Model for todos create request."""

    title: str
    description: str | None = None


class TodosAllFields(BaseModel):
    """Model for todos create response."""

    id: int
    title: str
    description: str | None
    finished: bool
    user: int


class TodosWithoutUser(BaseModel):
    """Todos model without user."""

    id: int
    title: str
    description: str | None
    finished: bool


class TodoUpdateIn(BaseModel):
    """Model for updating todo."""

    title: str
    description: str | None
    finished: bool
