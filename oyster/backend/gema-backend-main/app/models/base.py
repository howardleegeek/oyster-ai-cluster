from app.db.base import Base


class BaseTable(Base):
    __abstract__ = True

    def __repr__(self):
        """
        Returns a string representation of the model, including all fields.
        """
        return f"{self.__class__.__name__}({', '.join(f'{key}={value}' for key, value in self.__dict__.items() if not key.startswith('_'))})"

