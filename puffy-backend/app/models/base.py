from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import DeclarativeBase


Base = declarative_base()


class BaseTable(Base):
    __abstract__ = True
    def __init_subclass__(cls, **kwargs):
        # Ensure __tablename__ and columns are inherited
        pass

    def __repr__(self):
        """
        Returns a string representation of the model, including all fields.
        """
        return f"{self.__class__.__name__}({', '.join(f'{key}={value}' for key, value in self.__dict__.items() if not key.startswith('_'))})"

