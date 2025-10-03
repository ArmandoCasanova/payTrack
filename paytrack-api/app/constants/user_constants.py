from enum import Enum


class UserRoles(Enum):
    ADMIN = "admin"
    EMPLOYEE = "employee"


class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class ClientStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAYS_ON_TIME = "pays_on_time"
    BAD_DEBTOR = "bad_debtor"


class PaymentStatus(Enum):
    PAID = "paid"
    PENDING = "pending"
    OVERDUE = "overdue"
    PARTIAL = "partial"
    CANCELLED = "cancelled"


class PaymentMethod(Enum):
    CASH = "cash"
    TRANSFER = "transfer"
    CARD = "card"
    CHECK = "check"


class SupplierStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class SupplierType(Enum):
    SERVICE = "service"
    PRODUCT = "product"
    MAINTENANCE = "maintenance"
    OFFICE = "office"
    OTHER = "other"


class VerificationModels(Enum):
    VERIFICATION_CODE_MODEL = "VERIFICATION_CODE_MODEL"
    VERIFICATION_CODE_PASSWORD_RESET_MODEL = "VERIFICATION_CODE_PASSWORD_RESET_MODEL"