from enum import Enum, EnumMeta
from typing import Any


class ContainableEnumImpl(EnumMeta):
    def __contains__(cls, item: Any):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class ContainableEnum(Enum, metaclass=ContainableEnumImpl):
    """ContainableEnum supports "in" statement to test if a value is in the enum
    """
    pass
