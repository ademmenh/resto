from decimal import Decimal


class ItemNotFoundError(Exception):
    code = "ITEM_NOT_FOUND"

    def __init__(self, item_id: str) -> None:
        super().__init__(f'Item with id "{item_id}" not found')


class InsufficientQuantityError(Exception):
    code = "INSUFFICIENT_QUANTITY"

    def __init__(self, item_id: str, requested: Decimal, available: Decimal) -> None:
        super().__init__(f'Item "{item_id}": requested {requested}, only {available} available')
        self.requested = requested
        self.available = available
