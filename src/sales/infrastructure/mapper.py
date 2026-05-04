from sqlalchemy import Row

from src.sales.domain.entity import SaleEntity


class SaleMapper:
    @staticmethod
    def to_domain(row: Row) -> SaleEntity:
        return SaleEntity(
            id=row.id,
            client_id=row.client_id,
            meal_id=row.meal_id,
            quantity=row.quantity,
            unit_price=row.unit_price,
            total_price=row.total_price,
            status=row.status,  # type: ignore[arg-type]
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    @staticmethod
    def to_values(entity: SaleEntity) -> dict:
        return {
            "id": entity.id,
            "client_id": entity.client_id,
            "meal_id": entity.meal_id,
            "quantity": entity.quantity,
            "unit_price": entity.unit_price,
            "total_price": entity.total_price,
            "status": entity.status,
        }
