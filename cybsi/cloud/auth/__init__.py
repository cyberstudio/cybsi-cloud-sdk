"""Use this section of API operate auth information.
"""
from .api import AuthAPI
from .api_key import (
    APIKeyAuth,
    APIKeysAPI,
    APIKeyRegistrationView,
    APIKeyForm,
    APIKeyView,
)
from .permission import (
    ResourceAction,
    ResourcePermissionView,
    ResourcePermissionForm,
)
from .resource import (
    ResourcesAPI,
    ResourceView,
    ResourceRefView,
)
from .token import TokenType, TokenView
