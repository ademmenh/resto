from fastapi import HTTPException
from src.inventory.domain.errors import InsufficientQuantityError, ItemNotFoundError


class InventoryExceptionHandler:
    def __call__(self, exc: Exception) -> None:
        match exc:
            case ItemNotFoundError():
                raise HTTPException(
                    status_code=404,
                    detail=getattr(exc, "message", str(exc)),
                )
            case InsufficientQuantityError():
                raise HTTPException(
                    status_code=409,
                    detail=getattr(exc, "message", str(exc)),
                )
            case _:
                raise exc
