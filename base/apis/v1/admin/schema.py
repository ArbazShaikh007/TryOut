from marshmallow import Schema, fields, validate


class AdminSchema(Schema):
    firstname = fields.String(required=True, validate=validate.Length(min=1, max=50))
    lastname = fields.String(required=True, validate=validate.Length(min=1, max=50))
    email = fields.Email(required=True, validate=validate.Length(min=1, max=100))
    password = fields.String(required=True, validate=validate.Length(min=6, max=50))

class LoginSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(min=1, max=100))
    password = fields.String(required=True, validate=validate.Length(min=6, max=50))


# class ChangePasswordSchema(Schema):
#     current_password = fields.String(
#         required=True, validate=validate.Length(min=6, max=50)
#     )
#     new_password = fields.String(required=True, validate=validate.Length(min=6, max=50))
#
#
# class EditProfileSchema(Schema):
#     fname = fields.String(validate=validate.Length(max=50))
#     lname = fields.String(validate=validate.Length(max=50))
#     email = fields.Email(validate=validate.Length(max=100))
#     phone = fields.String(validate=validate.Length(max=12))
#
#
# class ResetPasswordRequestSchema(Schema):
#     email = fields.Email(required=True, validate=validate.Length(min=1, max=100))
#
#
# class ResetPasswordSchema(Schema):
#     reset_token = fields.String(required=True, validate=validate.Length(min=1))
#     new_password = fields.String(required=True, validate=validate.Length(min=6, max=50))
#
# class ContentSchema(Schema):
#     id = fields.Integer(dump_only=True)
#     content = fields.String(required=True, validate=validate.Length(min=1))
#     content_type = fields.String(
#         required=True,
#         validate=validate.OneOf(
#             [
#                 "user_terms",
#                 "user_privacy",
#
#             ]
#         ),
#     )
#     created_at = fields.DateTime(dump_only=True)
#     updated_at = fields.DateTime(dump_only=True)
