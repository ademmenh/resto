from sqlalchemy import Row

from src.meals.domain.entity import MealEntity


class MealMapper:
    @staticmethod
    def to_domain(row: Row) -> MealEntity:
        return MealEntity(
            id=row.id,
            name=row.name,
            description=row.description,
            price=row.price,
            category=row.category,
            available=row.available,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    @staticmethod
    def to_values(entity: MealEntity) -> dict:
        return {
            "id": entity.id,
            "name": entity.name,
            "description": entity.description,
            "price": entity.price,
            "category": entity.category,
            "available": entity.available,
        }
