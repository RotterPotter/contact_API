import sqlalchemy.orm as orm
import tests.testdatabase
from sqlalchemy_file import FileField

class Contact(tests.testdatabase.Base):
    __tablename__ = 'Contacts'

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    firstname: orm.Mapped[str]
    lastname: orm.Mapped[str]
    email: orm.Mapped[str] = orm.mapped_column(unique=True)
    phone: orm.Mapped[str] = orm.mapped_column(unique=True) 
    birthday: orm.Mapped[str]
    avatar: orm.Mapped[str | None] = orm.mapped_column(default=None)

