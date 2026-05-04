from fastapi import Depends, Query
from src.meals.application.create_meal import CreateMeal, CreateMealInput
from src.meals.application.delete_meal import DeleteMeal, DeleteMealInput
from src.meals.application.get_meal import GetMeal, GetMealInput
from src.meals.application.list_meals import ListMeals, ListMealsInput
from src.meals.application.update_meal import UpdateMeal, UpdateMealInput
from src.meals.domain.errors import MealNotFoundError
from src.meals.presentation.dtos import CreateMealDto, UpdateMealDto
from src.meals.presentation.exception_handler import MealsExceptionHandler
from src.meals.presentation.rdtos import MealRDTO
from src.auth.domain.ports import TokenPayload
from src.shared.presentation.responses import PaginatedResponse, PaginationMeta, Response
from typing import Annotated
from src.shared.presentation.auth import AccessTokenGuard, RoleGuard


class MealsController:
    def __init__(
        self,
        router,
        exception_handler: MealsExceptionHandler,
        list_meals_use_case: ListMeals,
        get_meal_use_case: GetMeal,
        create_meal_use_case: CreateMeal,
        update_meal_use_case: UpdateMeal,
        delete_meal_use_case: DeleteMeal,
    ) -> None:
        self.router = router
        self.exception_handler = exception_handler
        self.list_meals_use_case = list_meals_use_case
        self.get_meal_use_case = get_meal_use_case
        self.create_meal_use_case = create_meal_use_case
        self.update_meal_use_case = update_meal_use_case
        self.delete_meal_use_case = delete_meal_use_case
        self._register_routes()

    def _register_routes(self) -> None:
        self.router.get("/meals", response_model=PaginatedResponse[MealRDTO])(self.list_meals)
        self.router.get("/meals/{meal_id}", response_model=Response[MealRDTO])(self.get_meal)
        self.router.post("/meals", response_model=Response[MealRDTO], status_code=201)(
            self.create_meal
        )
        self.router.put("/meals/{meal_id}", response_model=Response[MealRDTO])(self.update_meal)
        self.router.delete("/meals/{meal_id}", status_code=204)(self.delete_meal)

    async def list_meals(
        self,
        _current_user: Annotated[TokenPayload, Depends(AccessTokenGuard())],
        _role: Annotated[str, Depends(RoleGuard(["admin"]))],
        page: Annotated[int, Query(ge=1, description="Page number")] = 1,
        limit: Annotated[int, Query(ge=1, le=32, description="Items per page")] = 20,
        category: str | None = None,
        available: bool | None = None,
        search: str | None = None,
    ) -> PaginatedResponse[MealRDTO]:
        try:
            meals, total = await self.list_meals_use_case.execute(
                ListMealsInput(
                    category=category,
                    available=available,
                    search=search,
                    page=page,
                    limit=limit,
                )
            )
            return PaginatedResponse(
                message="Meals retrieved successfully",
                status_code=200,
                data=[MealRDTO.from_entity(m) for m in meals],
                pagination=PaginationMeta(total=total, page=page, limit=limit),
            )
        except Exception:
            raise

    async def get_meal(
        self,
        meal_id: str,
        _current_user: Annotated[TokenPayload, Depends(AccessTokenGuard())],
        _role: Annotated[str, Depends(RoleGuard(["admin"]))],
    ) -> Response[MealRDTO]:
        try:
            meal = await self.get_meal_use_case.execute(GetMealInput(meal_id=meal_id))
            return Response(
                message="Meal retrieved successfully",
                status_code=200,
                data=MealRDTO.from_entity(meal),
            )
        except MealNotFoundError as exc:
            self.exception_handler(exc)

    async def create_meal(
        self,
        dto: CreateMealDto,
        _current_user: Annotated[TokenPayload, Depends(AccessTokenGuard())],
        _role: Annotated[str, Depends(RoleGuard(["admin"]))],
    ) -> Response[MealRDTO]:
        try:
            meal = await self.create_meal_use_case.execute(
                CreateMealInput(
                    name=dto.name,
                    description=dto.description,
                    price=dto.price,
                    category=dto.category,
                    available=dto.available,
                )
            )
            return Response(
                message="Meal created successfully",
                status_code=201,
                data=MealRDTO.from_entity(meal),
            )
        except Exception:
            raise

    async def update_meal(
        self,
        meal_id: str,
        dto: UpdateMealDto,
        _current_user: Annotated[TokenPayload, Depends(AccessTokenGuard())],
        _role: Annotated[str, Depends(RoleGuard(["admin"]))],
    ) -> Response[MealRDTO]:
        try:
            meal = await self.update_meal_use_case.execute(
                UpdateMealInput(
                    meal_id=meal_id,
                    name=dto.name,
                    description=dto.description,
                    price=dto.price,
                    category=dto.category,
                    available=dto.available,
                )
            )
            return Response(
                message="Meal updated successfully",
                status_code=200,
                data=MealRDTO.from_entity(meal),
            )
        except MealNotFoundError as exc:
            self.exception_handler(exc)

    async def delete_meal(
        self,
        meal_id: str,
        _current_user: Annotated[TokenPayload, Depends(AccessTokenGuard())],
        _role: Annotated[str, Depends(RoleGuard(["admin"]))],
    ) -> None:
        try:
            await self.delete_meal_use_case.execute(DeleteMealInput(meal_id=meal_id))
        except MealNotFoundError as exc:
            self.exception_handler(exc)
