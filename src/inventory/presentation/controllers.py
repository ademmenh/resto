from fastapi import Depends, Query
from src.inventory.application.add_quantity import AddQuantity, AddQuantityInput
from src.inventory.application.create_item import CreateItem, CreateItemInput
from src.inventory.application.delete_item import DeleteItem, DeleteItemInput
from src.inventory.application.get_item import GetItem, GetItemInput
from src.inventory.application.list_items import ListItems, ListItemsInput
from src.inventory.application.reduce_quantity import ReduceQuantity, ReduceQuantityInput
from src.inventory.application.update_item import UpdateItem, UpdateItemInput
from src.inventory.domain.errors import InsufficientQuantityError, ItemNotFoundError
from src.inventory.domain.unit import UnitValue
from src.inventory.presentation.dtos import CreateItemDto, QuantityChangeDto, UpdateItemDto
from src.inventory.presentation.rdtos import ItemRDTO
from src.auth.domain.ports import TokenPayload
from src.shared.presentation.responses import PaginatedResponse, PaginationMeta, Response
from typing import Annotated
from src.shared.presentation.auth import AccessTokenGuard, RoleGuard


class InventoryController:
    def __init__(
        self,
        router,
        exception_handler: any,
        id_generator: any,
        list_items_use_case: ListItems,
        get_item_use_case: GetItem,
        create_item_use_case: CreateItem,
        update_item_use_case: UpdateItem,
        add_quantity_use_case: AddQuantity,
        reduce_quantity_use_case: ReduceQuantity,
        delete_item_use_case: DeleteItem,
    ) -> None:
        self.router = router
        self.exception_handler = exception_handler
        self.id_generator = id_generator
        self.list_items_use_case = list_items_use_case
        self.get_item_use_case = get_item_use_case
        self.create_item_use_case = create_item_use_case
        self.update_item_use_case = update_item_use_case
        self.add_quantity_use_case = add_quantity_use_case
        self.reduce_quantity_use_case = reduce_quantity_use_case
        self.delete_item_use_case = delete_item_use_case
        self._register_routes()

    def _register_routes(self) -> None:
        self.router.get("/inventory/items", response_model=PaginatedResponse[ItemRDTO])(self.list_items)
        self.router.get("/inventory/items/{item_id}", response_model=Response[ItemRDTO])(self.get_item)
        self.router.post("/inventory/items", response_model=Response[ItemRDTO], status_code=201)(
            self.create_item
        )
        self.router.put("/inventory/items/{item_id}", response_model=Response[ItemRDTO])(self.update_item)
        self.router.post("/inventory/items/{item_id}/add-quantity", response_model=Response[ItemRDTO])(
            self.add_quantity
        )
        self.router.post("/inventory/items/{item_id}/reduce-quantity", response_model=Response[ItemRDTO])(
            self.reduce_quantity
        )
        self.router.delete("/inventory/items/{item_id}", status_code=204)(self.delete_item)

    async def list_items(
        self,
        _current_user: Annotated[TokenPayload, Depends(AccessTokenGuard())],
        _role: Annotated[str, Depends(RoleGuard(["admin"]))],
        page: Annotated[int, Query(ge=1, description="Page number")] = 1,
        limit: Annotated[int, Query(ge=1, le=32, description="Items per page")] = 20,
        unit: UnitValue | None = None,
        search: str | None = None,
    ) -> PaginatedResponse[ItemRDTO]:
        try:
            items, total = await self.list_items_use_case.execute(ListItemsInput(unit=unit, search=search, page=page, limit=limit))
            return PaginatedResponse(
                message="Items retrieved successfully",
                status_code=200,
                data=[ItemRDTO.from_entity(i) for i in items],
                pagination=PaginationMeta(total=total, page=page, limit=limit),
            )
        except Exception as exc:
            self.exception_handler(exc)

    async def get_item(
        self,
        item_id: str,
        _current_user: Annotated[TokenPayload, Depends(AccessTokenGuard())],
        _role: Annotated[str, Depends(RoleGuard(["admin"]))],
    ) -> Response[ItemRDTO]:
        try:
            item = await self.get_item_use_case.execute(GetItemInput(item_id=item_id))
            return Response(
                message="Item retrieved successfully",
                status_code=200,
                data=ItemRDTO.from_entity(item),
            )
        except ItemNotFoundError as exc:
            self.exception_handler(exc)

    async def create_item(
        self,
        dto: CreateItemDto,
        _current_user: Annotated[TokenPayload, Depends(AccessTokenGuard())],
        _role: Annotated[str, Depends(RoleGuard(["admin"]))],
    ) -> Response[ItemRDTO]:
        try:
            item = await self.create_item_use_case.execute(CreateItemInput(name=dto.name, quantity=dto.quantity, unit=dto.unit))
            return Response(
                message="Item created successfully",
                status_code=201,
                data=ItemRDTO.from_entity(item),
            )
        except Exception as exc:
            self.exception_handler(exc)

    async def update_item(
        self,
        item_id: str,
        dto: UpdateItemDto,
        _current_user: Annotated[TokenPayload, Depends(AccessTokenGuard())],
        _role: Annotated[str, Depends(RoleGuard(["admin"]))],
    ) -> Response[ItemRDTO]:
        try:
            item = await self.update_item_use_case.execute(UpdateItemInput(item_id=item_id, name=dto.name, unit=dto.unit))
            return Response(
                message="Item updated successfully",
                status_code=200,
                data=ItemRDTO.from_entity(item),
            )
        except ItemNotFoundError as exc:
            self.exception_handler(exc)

    async def add_quantity(
        self,
        item_id: str,
        dto: QuantityChangeDto,
        _current_user: Annotated[TokenPayload, Depends(AccessTokenGuard())],
        _role: Annotated[str, Depends(RoleGuard(["admin"]))],
    ) -> Response[ItemRDTO]:
        try:
            item = await self.add_quantity_use_case.execute(AddQuantityInput(item_id=item_id, amount=dto.amount))
            return Response(
                message="Quantity added successfully",
                status_code=200,
                data=ItemRDTO.from_entity(item),
            )
        except ItemNotFoundError as exc:
            self.exception_handler(exc)

    async def reduce_quantity(
        self,
        item_id: str,
        dto: QuantityChangeDto,
        _current_user: Annotated[TokenPayload, Depends(AccessTokenGuard())],
        _role: Annotated[str, Depends(RoleGuard(["admin"]))],
    ) -> Response[ItemRDTO]:
        try:
            item = await self.reduce_quantity_use_case.execute(ReduceQuantityInput(item_id=item_id, amount=dto.amount))
            return Response(
                message="Quantity reduced successfully",
                status_code=200,
                data=ItemRDTO.from_entity(item),
            )
        except (ItemNotFoundError, InsufficientQuantityError) as exc:
            self.exception_handler(exc)

    async def delete_item(
        self,
        item_id: str,
        _current_user: Annotated[TokenPayload, Depends(AccessTokenGuard())],
        _role: Annotated[str, Depends(RoleGuard(["admin"]))],
    ) -> None:
        try:
            await self.delete_item_use_case.execute(DeleteItemInput(item_id=item_id))
        except ItemNotFoundError as exc:
            self.exception_handler(exc)
