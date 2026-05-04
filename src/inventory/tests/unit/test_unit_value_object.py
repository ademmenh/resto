import pytest
from src.inventory.domain.unit import Unit


class TestUnitValueObject:
    @pytest.mark.parametrize("value", ["kg", "l", "m3", "g"])
    def test_known_values_are_accepted(self, value: str):
        unit = Unit.create(value)
        assert unit.value == value

    def test_unknown_value_raises(self):
        with pytest.raises(ValueError, match="Unknown unit"):
            Unit.create("oz")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            Unit.create("")

    def test_case_sensitive(self):
        with pytest.raises(ValueError):
            Unit.create("KG")

    def test_is_frozen(self):
        unit = Unit.create("kg")
        with pytest.raises((AttributeError, TypeError)):
            unit.value = "l"  # type: ignore[misc]

    def test_equal_units_are_equal(self):
        assert Unit.create("kg") == Unit.create("kg")

    def test_different_units_are_not_equal(self):
        assert Unit.create("kg") != Unit.create("g")

    def test_str_returns_value(self):
        assert str(Unit.create("l")) == "l"

    def test_repr_contains_value(self):
        assert "m3" in repr(Unit.create("m3"))
