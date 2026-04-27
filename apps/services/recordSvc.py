from apps.repositories.recordRepo import RecordRepository
from apps.services.accessControlSvc import AccessControlService
from apps.services.auditLogger import AuditLogger
from apps.security.masker import SensitiveDataMasker
from apps.security.tokenizer import Tokenizer


class RecordService:
    """
    Service responsible for secure record retrieval.

    This service combines data access, authorization, sensitive data
    protection, and audit logging into one controlled workflow.
    """

    def __init__(self) -> None:
        self.record_repository = RecordRepository()
        self.access_control_service = AccessControlService()
        self.audit_logger = AuditLogger()
        self.masker = SensitiveDataMasker()
        self.tokenizer = Tokenizer()

    def get_masked_record(self, user, record_id: int) -> dict:
        """
        Return a record only if the user is authorized.

        Before returning the data, this method masks or tokenizes sensitive
        fields so the interface does not expose raw confidential values.
        """
        if not self.access_control_service.is_authorized(
                user, "view_masked_record"):
            self.audit_logger.log_event(
                "access_denied", user.username, "failure")
            return {"status": "failure", "message": "Access denied"}

        record = self.record_repository.find_by_id(record_id)
        if record is None:
            self.audit_logger.log_event(
                "record_not_found", user.username, "failure")
            return {"status": "failure", "message": "Record not found"}

        protected_record = {
            "record_id": record.record_id,
            "patient_name": self.masker.mask_name(record.patient_name),
            "ssn_masked": self.masker.mask_ssn(record.ssn),
            "ssn_token": self.tokenizer.tokenize(record.ssn),
            "medical_notes": record.medical_notes,
        }

        self.audit_logger.log_event("record_access", user.username, "success")
        return {"status": "success", "record": protected_record}
