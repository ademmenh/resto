from dataclasses import dataclass
from src.meals.domain.errors import MealNotAvailableError, MealNotFoundError
from src.meals.domain.ports import IMealRepository
from src.sales.domain.entity import SaleEntity
from src.sales.domain.ports import ISaleRepository
from src.shared.infrastructure.id_generator import IDGenerator
from src.users.domain.errors import UserNotFoundError
from src.users.domain.ports import IUserRepository


@dataclass
class CreateSaleInput:
    client_id: str
    meal_id: str
    quantity: int


class CreateSale:
    def __init__(
        self,
        sale_repository: ISaleRepository,
        meal_repository: IMealRepository,
        user_repository: IUserRepository,
        id_generator: IDGenerator,
    ) -> None:
        self._sale_repository = sale_repository
        self._meal_repository = meal_repository
        self._user_repository = user_repository
        self._id_generator = id_generator

    async def execute(self, input: CreateSaleInput) -> SaleEntity:
        client = await self._user_repository.find_by_id(input.client_id)
        if client is None:
            raise UserNotFoundError(input.client_id)

        meal = await self._meal_repository.find_by_id(input.meal_id)
        if meal is None:
            raise MealNotFoundError(input.meal_id)
        if not meal.is_available():
            raise MealNotAvailableError(input.meal_id)

        sale_id = self._id_generator.generate()
        unit_price = meal.price
        total_price = unit_price * input.quantity

        sale = SaleEntity(
            id=sale_id.value,
            client_id=input.client_id,
            meal_id=input.meal_id,
            quantity=input.quantity,
            unit_price=unit_price,
            total_price=total_price,
        )

        return await self._sale_repository.create(sale)
