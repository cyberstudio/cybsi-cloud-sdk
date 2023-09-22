from typing import Optional, TypeVar, Union, cast


class Tag:
    """Identifier of a specific version of a resource.

    Prevents mid-air-collisions.
    Required for edit() functions on Cybsi Cloud API resources.
    """

    pass


# This is a hack to prevent Sphinx autodoc-typehint type inlining.
# If we simply alias Tag = str, it inlines str everywhere,
# and functions lose descriptive parameter and return value types.
# Additionally, this hack prevents SDK users from creating Tag instances.
# Users have to call view()-like methods.
Tag.__supertype__ = str  # type: ignore


class NullType:
    """Depicts explicit `null` values in API.

    The only instance of this type is :data:`Null`.
    """

    pass


Null = NullType()
"""The only possible value of :class:`NullType`"""

T = TypeVar("T")
"""Non-null type."""

Nullable = Union[T, None, NullType]
"""Missing JSON field and ``null`` JSON field sometimes
have a difference in Cybsi Cloud API.
Typically, ``register()`` or ``edit()``-like methods omit unset keyword parameters
when they send request to API.

Nullable is used to indicate optional keyword arguments
which are be passed as explicit ``null`` to API.
"""


# SDK internal function. Placed here for locality with Nullable.
def _unwrap_nullable(value: Nullable[T]) -> Optional[T]:
    return None if value is Null else cast(T, value)
