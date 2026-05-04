from .application.create_sale import CreateSale
from .application.get_sale import GetSale
from .application.list_sales import ListSales
from .application.update_sale import UpdateSale
from .infrastructure.repository import SaleRepository
from .presentation.controllers import SalesController
from .presentation.exception_handler import SalesExceptionHandler
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncEngine
from src.meals.infrastructure.repository import MealRepository
from src.shared.infrastructure.id_generator import IDGenerator
from src.users.infrastructure.repository import UserRepository


class SalesModule:
    def __init__(
        self,
        id_generator: IDGenerator,
        engine: AsyncEngine,
    ) -> None:
        router = APIRouter()
        sale_repo = SaleRepository(engine)
        meal_repo = MealRepository(engine)
        user_repo = UserRepository(engine)

        list_sales_use_case = ListSales(sale_repo)
        get_sale_use_case = GetSale(sale_repo)
        create_sale_use_case = CreateSale(sale_repo, meal_repo, user_repo, id_generator)
        update_sale_use_case = UpdateSale(sale_repo)

        exception_handler = SalesExceptionHandler()
        controller = SalesController(
            router=router,
            exception_handler=exception_handler,
            list_sales_use_case=list_sales_use_case,
            get_sale_use_case=get_sale_use_case,
            create_sale_use_case=create_sale_use_case,
            update_sale_use_case=update_sale_use_case,
        )
        self.router: APIRouter = controller.router
