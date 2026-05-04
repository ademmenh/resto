from fastapi import HTTPException
from src.meals.domain.errors import MealNotAvailableError, MealNotFoundError
from src.sales.domain.errors import (
    SaleAccessDeniedError,
    SaleCannotBeCancelledError,
    SaleNotFoundError,
)
from src.users.domain.errors import UserNotFoundError


class SalesExceptionHandler:
    def __call__(self, exc: Exception) -> None:
        match exc:
            case SaleNotFoundError():
                raise HTTPException(
                    status_code=404,
                    detail=getattr(exc, "message", str(exc)),
                )
            case SaleAccessDeniedError():
                raise HTTPException(
                    status_code=403,
                    detail=getattr(exc, "message", str(exc)),
                )
            case SaleCannotBeCancelledError():
                raise HTTPException(
                    status_code=422,
                    detail=getattr(exc, "message", str(exc)),
                )
            case MealNotFoundError():
                raise HTTPException(
                    status_code=404,
                    detail=getattr(exc, "message", str(exc)),
                )
            case MealNotAvailableError():
                raise HTTPException(
                    status_code=422,
                    detail=getattr(exc, "message", str(exc)),
                )
            case UserNotFoundError():
                raise HTTPException(
                    status_code=404,
                    detail=getattr(exc, "message", str(exc)),
                )
            case _:
                raise exc
