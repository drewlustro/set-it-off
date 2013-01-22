from flask.ext.wtf import Form, TextField, Required, PasswordField, Length,\
                         Email


class SignupForm(Form):
    email = TextField("E-Mail", validators=[Required(), Email()])
    password = PasswordField("Choose Password",
            validators=[Required(), Length(min=4,
        max=50)])
