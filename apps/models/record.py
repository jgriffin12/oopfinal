from dataclasses import dataclass


@dataclass
class Record:
    """
    Record model.

    This represents sensitive healthcare-style information. In the real
    project, these fields could represent patient or employee data that
    must be protected before being shown in the UI.
    """
    record_id: int
    patient_name: str
    ssn: str
    medical_notes: str

    def get_summary(self) -> str:
        """
        Return a simple string summary of the record.

        This is useful for debugging or lightweight display.
        """
        return f"Record {self.record_id} for {self.patient_name}"
