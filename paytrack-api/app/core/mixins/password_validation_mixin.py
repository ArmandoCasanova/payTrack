import re

from pydantic import BaseModel, Field, field_validator, model_validator

from app.utils.regex import Regex

from app.core.http_response import PayTrackHttpResponse
from app.constants.response_codes import PayTrackResponseCodes


class PasswordValidationMixin(BaseModel):
    password: str = Field(min_length=8, max_length=20)
    confirm_password: str = Field(min_length=8, max_length=20)

    @field_validator("password")
    @classmethod
    def validate_password_fields(cls, p: str) -> str:
        re_for_pw: re.Pattern[str] = re.compile(Regex.PASSWORD)
        if not re_for_pw.match(p):
            raise ValueError(PayTrackResponseCodes.INVALID_PASSWORD.detail)
        return p

    @model_validator(mode="after")
    def passwords_match(self) -> "PasswordValidationMixin":
        if self.password != self.confirm_password:
            PayTrackHttpResponse.forbidden(
                data={
                    "message": PayTrackResponseCodes.INVALID_PASSWORDS_MATCH.detail,
                },
                error_id=PayTrackResponseCodes.INVALID_PASSWORDS_MATCH.code,
            )
        return self
