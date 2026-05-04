from .application.add_quantity import AddQuantity
from .application.create_item import CreateItem
from .application.delete_item import DeleteItem
from .application.get_item import GetItem
from .application.list_items import ListItems
from .application.reduce_quantity import ReduceQuantity
from .application.update_item import UpdateItem
from .infrastructure.repository import ItemRepository
from .presentation.controllers import InventoryController
from .presentation.exception_handler import InventoryExceptionHandler
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncEngine
from src.shared.infrastructure.id_generator import IDGenerator


class InventoryModule:
    def __init__(
        self,
        id_generator: IDGenerator,
        engine: AsyncEngine,
    ) -> None:
        router = APIRouter()
        item_repo = ItemRepository(engine)

        list_items_use_case = ListItems(item_repo)
        get_item_use_case = GetItem(item_repo)
        create_item_use_case = CreateItem(item_repo, id_generator)
        update_item_use_case = UpdateItem(item_repo)
        add_quantity_use_case = AddQuantity(item_repo)
        reduce_quantity_use_case = ReduceQuantity(item_repo)
        delete_item_use_case = DeleteItem(item_repo)

        exception_handler = InventoryExceptionHandler()
        controller = InventoryController(
            router=router,
            exception_handler=exception_handler,
            id_generator=id_generator,
            list_items_use_case=list_items_use_case,
            get_item_use_case=get_item_use_case,
            create_item_use_case=create_item_use_case,
            update_item_use_case=update_item_use_case,
            add_quantity_use_case=add_quantity_use_case,
            reduce_quantity_use_case=reduce_quantity_use_case,
            delete_item_use_case=delete_item_use_case,
        )
        self.router: APIRouter = controller.router
