class SaleNotFoundError(Exception):
    code = "SALE_NOT_FOUND"

    def __init__(self, sale_id: str) -> None:
        super().__init__(f'Sale with id "{sale_id}" not found')


class SaleAccessDeniedError(Exception):
    code = "SALE_ACCESS_DENIED"

    def __init__(self) -> None:
        super().__init__("You do not have access to this sale")


class SaleCannotBeCancelledError(Exception):
    code = "SALE_CANNOT_BE_CANCELLED"

    def __init__(self) -> None:
        super().__init__("Only pending sales can be cancelled")
