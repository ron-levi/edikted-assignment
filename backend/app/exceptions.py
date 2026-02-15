class AppException(Exception):
    def __init__(self, status_code: int, error_code: str, detail: str):
        self.status_code = status_code
        self.error_code = error_code
        self.detail = detail
        super().__init__(detail)


class NotFoundError(AppException):
    def __init__(self, entity: str, entity_id: int):
        super().__init__(
            status_code=404,
            error_code="NOT_FOUND",
            detail=f"{entity} with ID {entity_id} not found",
        )


class InvalidTransitionError(AppException):
    def __init__(self, current_state: str, target_state: str, valid_targets: list[str]):
        super().__init__(
            status_code=409,
            error_code="INVALID_TRANSITION",
            detail=f"Cannot transition from {current_state} to {target_state}. Valid transitions: {valid_targets}",
        )


class IncompatibleAttributeError(AppException):
    def __init__(self, attribute_name: str, conflicting_names: list[str]):
        super().__init__(
            status_code=409,
            error_code="INCOMPATIBLE_ATTRIBUTE",
            detail=f"Attribute '{attribute_name}' is incompatible with existing attributes: {', '.join(conflicting_names)}",
        )


class DeletionProtectedError(AppException):
    def __init__(self, garment_name: str):
        super().__init__(
            status_code=403,
            error_code="DELETION_PROTECTED",
            detail=f"Garment '{garment_name}' is in PRODUCTION stage and cannot be deleted.",
        )


class ValidationError(AppException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=422,
            error_code="VALIDATION_ERROR",
            detail=detail,
        )
