from enum import Enum


class UserRoles(Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"
    STAFF = "staff"


class VerificationModels(Enum):
    VERIFICATION_CODE_MODEL = "VERIFICATION_CODE_MODEL"
    VERIFICATION_CODE_PASSWORD_RESET_MODEL = "VERIFICATION_CODE_PASSWORD_RESET_MODEL"