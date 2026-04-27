from apps.models.record import Record


class RecordRepository:
    """
    Repository responsible for record data access.

    This starter version uses in-memory data so the project can run before
    the database layer is implemented.
    """

    def __init__(self) -> None:
        self.records = {
            1: Record(
                record_id=1,
                patient_name="Alice Anderson",
                ssn="123-45-6789",
                medical_notes="Patient has a follow-up appointment next week.",
            ),
            2: Record(
                record_id=2,
                patient_name="Bob Brown",
                ssn="987-65-4321",
                medical_notes="Patient is recovering well after treatment.",
            ),
        }

    def find_by_id(self, record_id: int):
        """
        Return the record if it exists, otherwise return None.
        """
        return self.records.get(record_id)
