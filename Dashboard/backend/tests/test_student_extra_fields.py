from app.schemas.schemas import StudentCreate
from app.services.dashboard_service import apply_student_extra_fields


class _FakeStudent:
    def __init__(self) -> None:
        self.extra_fields: dict = {"grade": "10", "district": "Colombo"}
        self.school = None
        self.district = "Colombo"


def test_apply_extra_fields_merges_without_wiping_other_keys():
    student = _FakeStudent()
    apply_student_extra_fields(student, {"school": "Royal"})
    assert student.extra_fields["grade"] == "10"
    assert student.extra_fields["district"] == "Colombo"
    assert student.extra_fields["school"] == "Royal"
    assert student.school == "Royal"
    assert student.district == "Colombo"


def test_apply_extra_fields_dual_writes_district_and_clears_empty():
    student = _FakeStudent()
    apply_student_extra_fields(student, {"district": "", "stream": "Physical"})
    assert "district" not in student.extra_fields
    assert student.district is None
    assert student.extra_fields["stream"] == "Physical"
    assert student.extra_fields["grade"] == "10"


def test_student_create_accepts_extra_fields():
    payload = StudentCreate(
        tenant_id="tenant-demo-physics",
        phone="0771234567",
        extra_fields={"school": "Royal", "district": "Colombo"},
    )
    assert payload.extra_fields["school"] == "Royal"
    assert payload.school is None
