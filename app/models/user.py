import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from flaskext.bcrypt import Bcrypt
from app.lib.database import Base, db
from app.models import Question, Entry


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False)
    password = Column(String(64))
    is_admin = Column(Boolean(), default=False, nullable=False)
    deleted = Column(Boolean(), default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # ------------------------------------------------------------------------
    # FIND / CREATE
    # ------------------------------------------------------------------------

    @staticmethod
    def find_by_email(email):
        return db.query(User).filter_by(email=email, deleted=False).first()

    @staticmethod
    def create(**kwargs):
        """Create and return a user.
        Pass in password as 'passwd'
        Returns:
            User object on success.
            False if email is taken.
        """
        if User.find_by_email(kwargs['email']):
            return False

        u = User(**kwargs)
        db.add(u)
        db.commit()
        return u

    @staticmethod
    def login(email, password):
        """Tries to log in a user

        Args:
            email_or_username: obvi.
            password: plaintext plaintext password

        Returns:
            User object if login succeeded
            False if login failed
        """
        ret = False
        bcrypt = Bcrypt()
        user = User.find_by_email(email)
        if user and bcrypt.check_password_hash(user.password, password):
            ret = user
        return ret

    # ------------------------------------------------------------------------
    # PASSWORD
    # ------------------------------------------------------------------------

    @property
    def passwd(self):
        return self.password

    @passwd.setter
    def passwd(self, value=None):
        bcrypt = Bcrypt()
        password = bcrypt.generate_password_hash(value)
        self.password = password

