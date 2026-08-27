from services.admissions.field_definitions import merge_column_backed_fields


def test_merge_dual_writes_school_and_district_into_extra():
    school, district, extra = merge_column_backed_fields(
        school="Royal College",
        district="Colombo",
        extra_fields={"parent_contact": "0771234567"},
    )
    assert school == "Royal College"
    assert district == "Colombo"
    assert extra["school"] == "Royal College"
    assert extra["district"] == "Colombo"
    assert extra["parent_contact"] == "0771234567"


def test_merge_copies_column_keys_from_extra_when_args_missing():
    school, district, extra = merge_column_backed_fields(
        school=None,
        district=None,
        extra_fields={"school": "Visakha", "stream": "Physical"},
    )
    assert school == "Visakha"
    assert district is None
    assert extra["school"] == "Visakha"
    assert extra["stream"] == "Physical"
    assert "district" not in extra
