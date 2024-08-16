import enum

from cryptography.fernet import Fernet
from sqlalchemy import Dialect, ForeignKey, LargeBinary, String, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base
from src.settings import Settings


class EncryptedType(TypeDecorator[str]):
    """Type for hashing password in a db."""

    # Specifies that the underlying column type is LargeBinary,
    # suitable for storing encrypted data
    impl = LargeBinary

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        self.fernet = Fernet(Settings.get_settings().FERNET_KEY)
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value: str | None, dialect: Dialect) -> bytes | None:
        """Takes input value and encrypts it.

        Args:
            value (value: str | None): input value
            dialect (Dialect): abstraction that encapsulates
                the details of a specific db

        Returns:
            bytes | None: Encrypted value when input values is correct else None
        """
        if value is not None:
            encrypted_value: bytes = self.fernet.encrypt(value.encode())
            return encrypted_value

        return value

    def process_result_value(self, value: bytes | None, dialect: Dialect) -> str | None:
        """Returns decrypted value."""
        if value is not None:
            return self.fernet.decrypt(value).decode()
        return value


class RoleEnum(enum.Enum):
    """Enum for role in Users model."""

    USER = "user"
    ADMIN = "admin"


class Users(Base):
    """Users model."""

    __tablename__: str = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(40), nullable=False)
    last_name: Mapped[str] = mapped_column(String(40), default="")
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(EncryptedType, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=False, nullable=False)
    role: Mapped[RoleEnum] = mapped_column(default=RoleEnum.USER, nullable=False)

    @property
    def is_admin(self) -> bool:
        """Check if the user is an admin."""
        return self.role == RoleEnum.ADMIN


class Todo(Base):
    """Todo note model."""

    __tablename__: str = "todo"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    finished: Mapped[bool] = mapped_column(default=False, nullable=False)
    user: Mapped[int] = mapped_column(ForeignKey("users.id"))
