import sqlalchemy.orm as orm
import database


class User(database.Base):
    __tablename__ = 'users'

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    username: orm.Mapped[str] = orm.mapped_column(unique=True)
    hashed_password: orm.Mapped[str]
    access_token: orm.Mapped[str | None] = orm.mapped_column(default=None)
    verified: orm.Mapped[bool] = orm.mapped_column(default=False)

class EmailToken(database.Base):
    __tablename__ = 'email_tokens'

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    username: orm.Mapped[str] = orm.mapped_column(default=True)
    email_token: orm.Mapped[str]