from flask_restx import fields

from . import create_email_field, ModelCreator, PASSWORD_EXAMPLE, create_id_field


class UserIdModel(ModelCreator):
    id = create_id_field(
        required=True,
        description="User`s ID in database"
    )


class EmailModel(ModelCreator):
    email = create_email_field(
        required=True,
        description="User`s email (login)"
    )


class PasswordModel(ModelCreator):
    password = fields.String(
        required=True,
        description='User`s password',
        example=PASSWORD_EXAMPLE,
        min_length=8,
        max_length=64
    )


class NameModel(ModelCreator):
    first_name = fields.String(
        required=False,
        description='User`s first name',
        example='Ivan',
        min_length=3,
        max_length=32
    )
    last_name = fields.String(
        required=False,
        description='User`s last name',
        example='Ivanov',
        min_length=3,
        max_length=32
    )


class AuthModel(PasswordModel, EmailModel):
    pass


class SignUpModel(PasswordModel, EmailModel, NameModel):
    pass


class AccountEditModel(EmailModel, NameModel):
    pass


class AccountModel(EmailModel, NameModel, UserIdModel):
    pass