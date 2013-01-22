from flask.ext.wtf import Form, TextField, PasswordField, Required


class LoginForm(Form):
    email = TextField("Email", validators=[Required()])
    password = PasswordField("Password", validators=[Required()])
