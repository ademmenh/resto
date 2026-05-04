from fastapi import HTTPException
from src.meals.domain.errors import MealNotAvailableError, MealNotFoundError


class MealsExceptionHandler:
    def __call__(self, exc: Exception) -> None:
        match exc:
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
            case _:
                raise exc
