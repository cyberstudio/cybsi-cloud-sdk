from typing import Iterable, Tuple

from enum_tools import document_enum

from ..enum import CybsiAPIEnum
from ..internal import BaseAPI, JsonObject


@document_enum
class ObjectKeyType(CybsiAPIEnum):
    """Object key type."""

    MD5Hash = "MD5Hash"
    SHA1Hash = "SHA1Hash"
    SHA256Hash = "SHA256Hash"
    SHA512Hash = "SHA512Hash"
    DomainName = "DomainName"
    URL = "URL"
    IPAddress = "IPAddress"
    IPNetwork = "IPNetwork"


@document_enum
class ObjectType(CybsiAPIEnum):
    """Object type."""

    File = "File"
    DomainName = "DomainName"
    URL = "URL"
    IPAddress = "IPAddress"
    IPNetwork = "IPNetwork"


class ObjectsAPI(BaseAPI):
    """Objects API."""

    _path = "/iocean/collections/{}/objects"

    def add(
        self,
        *,
        collection_id: str,
        obj_type: ObjectType,
        keys: Iterable[Tuple[ObjectKeyType, str]],
        context: JsonObject = {},
    ):
        """Add object to collection.

        If there is registered object with corresponding keys
        and there are no keys conflicts, this method:
        - rewrites object context with new one;
        - extends key set of the registered object.

        Note:
            Calls `POST /iocean/collections/{collection_id}/objects`.
        Args:
            collection_id: Collection identifier.
            obj_type: Type of the object.
            keys: Keys of the object.
            context: Additional data describing object.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.NotFoundError`: Collection not found.
            :class:`~cybsi.cloud.error.SemanticError`: Request contains logic errors.
        Note:
            Semantic error codes specific for this method:
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidKeyFormat`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidKeySet`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.KeySetConflict`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.SchemaCheckFail`
        """
        path = self._path.format(collection_id)
        payload = {
            "type": obj_type.value,
            "keys": [{"type": key[0].value, "value": key[1]} for key in keys],
            "context": context,
        }
        self._connector.do_post(path=path, json=payload)

    def delete(
        self,
        *,
        collection_id: str,
        key_type: ObjectKeyType,
        key_value: str,
    ):
        """Delete object from collection.

        Note:
            Calls `DELETE /iocean/collections/{collection_id}/objects`.
        Args:
            collection_id: Collection identifier.
            key_type: Key type of object to be removed.
            key_value: Key value of object to be removed.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.NotFoundError`: Collection not found.
            :class:`~cybsi.cloud.error.SemanticError`: Request contains logic errors.
        Note:
            Semantic error codes specific for this method:
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidKeyFormat`
        """
        params: JsonObject = {
            "objectKeyType": key_type.value,
            "objectKey": key_value,
        }
        path = self._path.format(collection_id)
        self._connector.do_delete(path=path, params=params)
