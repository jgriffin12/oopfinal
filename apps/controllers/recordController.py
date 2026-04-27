from apps.services.recordSvc import RecordService
from apps.repositories.userRepo import UserRepository


class RecordController:
    """
    Controller for protected record requests.

    The controller accepts data from the route layer and delegates the
    actual business logic to the service layer.
    """

    def __init__(self) -> None:
        self.record_service = RecordService()
        self.user_repository = UserRepository()

    def get_record(self, record_id: int, username: str) -> dict:
        """
        Look up the requesting user, then delegate secure record retrieval
        to the service layer.
        """
        user = self.user_repository.find_by_username(username)

        if user is None:
            return {"status": "failure", "message": "User not found"}

        return self.record_service.get_masked_record(user, record_id)
