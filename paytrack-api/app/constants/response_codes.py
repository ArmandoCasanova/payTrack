class ResponseCode:
    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail


class PayTrackResponseCodes:
    @staticmethod
    def create_response_code(code: str, detail: str) -> ResponseCode:
        """Create response code method"""
        return ResponseCode(code, detail)

    INVALID_DATE_BIRTH_PAYLOAD = create_response_code("E001", "Invalid birth date")
    INVALID_PASSWORD = create_response_code("E002", "Invalid password")
    EXISTING_EMAIL = create_response_code("E003", "User with this email already exists")
    INVALID_PASSWORDS_MATCH = create_response_code("E006", "Passwords does not match")
    UNEXISTING_CODE = create_response_code("E007", "Code with this id does not exist")
    ALREADY_USED_CODE = create_response_code("E008", "Code has already been used")
    VERIFIED_USER = create_response_code("E009", "User verified successfully")
    UNEXISTING_USER = create_response_code("E010", "User does not exist")
    UNVERIFIED_USER = create_response_code("E011", "User is not verified")
    INVALID_CODE = create_response_code("E012", "Invalid code")

