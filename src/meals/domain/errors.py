class MealNotFoundError(Exception):
    code = "MEAL_NOT_FOUND"

    def __init__(self, meal_id: str) -> None:
        super().__init__(f'Meal with id "{meal_id}" not found')


class MealNotAvailableError(Exception):
    code = "MEAL_NOT_AVAILABLE"

    def __init__(self, meal_id: str) -> None:
        super().__init__(f'Meal with id "{meal_id}" is not available')
