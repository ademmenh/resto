from .application.create_meal import CreateMeal
from .application.delete_meal import DeleteMeal
from .application.get_meal import GetMeal
from .application.list_meals import ListMeals
from .application.update_meal import UpdateMeal
from .infrastructure.repository import MealRepository
from .presentation.controllers import MealsController
from .presentation.exception_handler import MealsExceptionHandler
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncEngine
from src.shared.infrastructure.id_generator import IDGenerator


class MealsModule:
    def __init__(
        self,
        id_generator: IDGenerator,
        engine: AsyncEngine,
    ) -> None:
        router = APIRouter()
        meal_repo = MealRepository(engine)

        list_meals_use_case = ListMeals(meal_repo)
        get_meal_use_case = GetMeal(meal_repo)
        create_meal_use_case = CreateMeal(meal_repo, id_generator)
        update_meal_use_case = UpdateMeal(meal_repo)
        delete_meal_use_case = DeleteMeal(meal_repo)

        exception_handler = MealsExceptionHandler()
        controller = MealsController(
            router=router,
            exception_handler=exception_handler,
            list_meals_use_case=list_meals_use_case,
            get_meal_use_case=get_meal_use_case,
            create_meal_use_case=create_meal_use_case,
            update_meal_use_case=update_meal_use_case,
            delete_meal_use_case=delete_meal_use_case,
        )
        self.router: APIRouter = controller.router
