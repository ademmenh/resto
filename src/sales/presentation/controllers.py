from fastapi import Depends, Query
from src.meals.domain.errors import MealNotAvailableError, MealNotFoundError
from src.sales.application.create_sale import CreateSale, CreateSaleInput
from src.sales.application.get_sale import GetSale, GetSaleInput
from src.sales.application.list_sales import ListSales, ListSalesInput
from src.sales.application.update_sale import UpdateSale, UpdateSaleInput
from src.sales.domain.errors import (
    SaleAccessDeniedError,
    SaleCannotBeCancelledError,
    SaleNotFoundError,
)
from src.sales.presentation.dtos import CreateSaleDto, UpdateSaleDto
from src.sales.presentation.exception_handler import SalesExceptionHandler
from src.sales.presentation.rdtos import SaleRDTO
from src.shared.presentation.auth import AccessTokenGuard
from src.auth.domain.ports import TokenPayload
from src.shared.presentation.responses import PaginatedResponse, PaginationMeta, Response
from src.users.domain.errors import UserNotFoundError
from typing import Annotated


class SalesController:
    def __init__(
        self,
        router,
        exception_handler: SalesExceptionHandler,
        list_sales_use_case: ListSales,
        get_sale_use_case: GetSale,
        create_sale_use_case: CreateSale,
        update_sale_use_case: UpdateSale,
    ) -> None:
        self.router = router
        self.exception_handler = exception_handler
        self.list_sales_use_case = list_sales_use_case
        self.get_sale_use_case = get_sale_use_case
        self.create_sale_use_case = create_sale_use_case
        self.update_sale_use_case = update_sale_use_case
        self._register_routes()

    def _register_routes(self) -> None:
        self.router.get("/sales", response_model=PaginatedResponse[SaleRDTO])(self.list_sales)
        self.router.get("/sales/{sale_id}", response_model=Response[SaleRDTO])(self.get_sale)
        self.router.post("/sales", response_model=Response[SaleRDTO], status_code=201)(
            self.create_sale
        )
        self.router.put("/sales/{sale_id}", response_model=Response[SaleRDTO])(self.update_sale)

    async def list_sales(
        self,
        current_user: Annotated[TokenPayload, Depends(AccessTokenGuard())],
        page: Annotated[int, Query(ge=1, description="Page number")] = 1,
        limit: Annotated[int, Query(ge=1, le=32, description="Items per page")] = 20,
        status: str | None = None,
    ) -> PaginatedResponse[SaleRDTO]:
        try:
            sales, total = await self.list_sales_use_case.execute(
                ListSalesInput(
                    requester_id=current_user.sub,
                    requester_role=current_user.role,
                    status=status,
                    page=page,
                    limit=limit,
                )
            )
            return PaginatedResponse(
                message="Sales retrieved successfully",
                status_code=200,
                data=[SaleRDTO.from_entity(s) for s in sales],
                pagination=PaginationMeta(total=total, page=page, limit=limit),
            )
        except Exception:
            raise

    async def get_sale(
        self,
        sale_id: str,
        current_user: Annotated[TokenPayload, Depends(AccessTokenGuard())],
    ) -> Response[SaleRDTO]:
        try:
            sale = await self.get_sale_use_case.execute(
                GetSaleInput(
                    sale_id=sale_id,
                    requester_id=current_user.sub,
                    requester_role=current_user.role,
                )
            )
            return Response(
                message="Sale retrieved successfully",
                status_code=200,
                data=SaleRDTO.from_entity(sale),
            )
        except (SaleNotFoundError, SaleAccessDeniedError) as exc:
            self.exception_handler(exc)

    async def create_sale(
        self,
        dto: CreateSaleDto,
        current_user: Annotated[TokenPayload, Depends(AccessTokenGuard())],
    ) -> Response[SaleRDTO]:
        try:
            sale = await self.create_sale_use_case.execute(
                CreateSaleInput(
                    client_id=current_user.sub,
                    meal_id=dto.meal_id,
                    quantity=dto.quantity,
                )
            )
            return Response(
                message="Sale created successfully",
                status_code=201,
                data=SaleRDTO.from_entity(sale),
            )
        except (MealNotFoundError, MealNotAvailableError, UserNotFoundError) as exc:
            self.exception_handler(exc)

    async def update_sale(
        self,
        sale_id: str,
        dto: UpdateSaleDto,
        current_user: Annotated[TokenPayload, Depends(AccessTokenGuard())],
    ) -> Response[SaleRDTO]:
        try:
            sale = await self.update_sale_use_case.execute(
                UpdateSaleInput(
                    sale_id=sale_id,
                    status=dto.status,
                )
            )
            return Response(
                message="Sale updated successfully",
                status_code=200,
                data=SaleRDTO.from_entity(sale),
            )
        except (SaleNotFoundError, SaleCannotBeCancelledError) as exc:
            self.exception_handler(exc)
