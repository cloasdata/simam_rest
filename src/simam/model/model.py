import datetime

from sqlalchemy import (Boolean, Column, Integer, String, DateTime, ForeignKey, Text, select, Table, func, desc)
from sqlalchemy.orm import relationship, declarative_base
from starlite import DTOFactory
from starlite.plugins.sql_alchemy import SQLAlchemyPlugin

from src.simam.database.session import session

Base = declarative_base()

dto_factory = DTOFactory(plugins=[SQLAlchemyPlugin()])

permission_role_map = Table('sa_permission_role_map', Base.metadata,
                      Column('permission_id', ForeignKey('sa_permission.id'), primary_key=True),
                      Column('role_id', ForeignKey('sa_role.id'), primary_key=True)
                      )


class Permission(Base):
    __tablename__ = "sa_permission"
    id = Column(Integer(), primary_key=True)
    name: String = Column(String(), nullable=False)

    roles = relationship("Role", secondary=permission_role_map, back_populates="permissions")

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Permission(permission={self.name})"


user_role_map = Table('sa_user_role_map', Base.metadata,
                      Column('user_id', ForeignKey('sa_user.id'), primary_key=True),
                      Column('role_id', ForeignKey('sa_role.id'), primary_key=True)
                      )


class Role(Base):
    """
    Each user can have more roles.
    To mange this we have user_role_map above
    """
    __tablename__ = "sa_role"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("sa_user.id"))
    name: String = Column(String(100))
    order: int = Column(Integer(), default=0)
    user: "User" = relationship('User', secondary=user_role_map, back_populates="roles")
    permissions: list[Permission] = relationship("Permission", secondary=permission_role_map, back_populates="roles")

    def __repr__(self):
        return f"Role(name={self.name}, order={self.order})"

    def __str__(self):
        return f"{self.name}"


class User(Base):
    __tablename__ = "sa_user"
    id = Column(Integer(), primary_key=True)
    first_name = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    login_name = Column(String(100), nullable=False, unique=True)
    email = Column(String(100), nullable=False)
    password = Column(String(), nullable=False)
    password_updated = Column(DateTime(), default=datetime.datetime(1970, 1, 1))
    last_login = Column(DateTime(), default=datetime.datetime(1970, 1, 1))
    deactivated = Column(Boolean(), default=False)

    created_by_id = Column(Integer(), ForeignKey(id))

    created_on = Column(DateTime(), default=datetime.datetime.now)
    update_on = Column(DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)

    vitae = Column(Text())

    created_by: "User" = relationship("User", uselist=False)

    projects: list["Project"] = relationship('Project', secondary="sa_project_team", back_populates="members")

    roles: list[Role] = relationship('Role', secondary=user_role_map, back_populates="user")

    messages: list["Message"] = relationship("Message", back_populates="sender")

    recipient: "Recipient" = relationship("Recipient", back_populates="user", uselist=False)

    def __str__(self):
        return f"User({self.first_name=}, {self.name=}, {self.login_name=})"

    def has_permission(self, permission: Permission) -> bool:
        permissions = []
        for role in self.roles:
            permissions.extend(role.permissions)
        return permission.id in [p.id for p in permissions]

    def has_project(self, project_id: int) -> bool:
        project_id = int(project_id)
        for project in self.projects:
            if project.id == project_id:
                return True
        return False


def get_user_by_name(login_name: str) -> User:
    return session.execute(select(User).where(User.login_name == login_name)).scalar_one_or_none()


def get_user_by_id(id_: str) -> User:
    return session.execute(select(User).where(User.id == int(id_))).scalar_one_or_none()


async def get_users() -> list["UserDTO"]:
    return [await UserDTO.from_model_instance_async(user) for user in session.execute(select(User)).scalars().all()]


class ProjectTeam(Base):
    """Many to Many"""
    __tablename__ = "sa_project_team"
    user_id = Column(Integer(), ForeignKey('sa_user.id'), primary_key=True)
    project_id = Column(Integer(), ForeignKey('sa_project.id'), primary_key=True)
    user: list["User"] = relationship("User", viewonly=True)
    project: "Project" = relationship("Project", viewonly=True)


class Project(Base):
    __tablename__ = "sa_project"
    id = Column(Integer(), primary_key=True)
    name = Column(String(255))
    short_name = Column(String(100), nullable=False)
    costcenter = Column(String(20), nullable=False)
    start_date = Column(DateTime(), default=datetime.datetime.now)
    scheduled_end_date = Column(DateTime(), default=datetime.datetime.now)
    actual_end_date = Column(DateTime(), default=datetime.datetime.now)

    created_by_id = Column(Integer(), ForeignKey("sa_user.id"))
    created_on = Column(DateTime(), default=datetime.datetime.now)
    update_on = Column(DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)

    created_by = relationship("User", uselist=False)

    messages: list["Message"] = relationship("Message", back_populates="project")
    members: list["User"] = relationship('User', secondary="sa_project_team", back_populates="projects")


def get_project(id_: str) -> Project:
    return session.execute(select(Project).where(Project.id == int(id_))).scalar_one_or_none()


class Recipient(Base):
    __tablename__ = "sa_recipient"
    user_id = Column(Integer, ForeignKey("sa_user.id"), primary_key=True)
    message_id = Column(Integer, ForeignKey("sa_message.id"), primary_key=True)
    send = Column(DateTime, default=datetime.datetime.now())
    transmitted = Column(DateTime)
    read = Column(DateTime)
    message: "Message" = relationship("Message", back_populates="recipients", uselist=False)
    user: "User" = relationship("User", back_populates="recipient", uselist=False)


class Message(Base):
    __tablename__ = "sa_message"
    id = Column(Integer(), primary_key=True)
    sender_id = Column(Integer(), ForeignKey("sa_user.id"), nullable=False)
    project_id = Column(Integer(), ForeignKey("sa_project.id"))
    issue_date = Column(DateTime(), default=datetime.datetime.now())
    edit_date = Column(DateTime())
    message_text: str = Column(Text())
    sender: "User" = relationship("User", back_populates="messages")
    project: "Project" = relationship("Project", back_populates="messages")
    recipients: list[Recipient] = relationship("Recipient", back_populates="message")

    def __str__(self):
        return f"Message({self.sender=}, {self.project=}, {self.message_text[:5]=})"


    def send_to_project_members(self, project_id: int = None):
        if project_id:
            self.project_id = project_id
        for user in self.project.members:
            self.recipients.append(
                Recipient(
                    message_id=self.id,
                    user_id=user.id
                )
            )
        session.commit()

    def transmit(self, user: "User"):
        for recipient in self.recipients:
            if recipient.user.id == user.id:
                recipient.transmitted = datetime.datetime.now()
                session.commit()
                return
        else:
            raise AttributeError(
                f"User {user} not found in message {self} recipients {self.recipients}."
            )


def get_message_by_project(project_id: int) -> list[Message]:
    cmd = select(Message).where(Message.project_id == project_id)
    return session.execute(cmd).scalars()


def filter_message(project_id: int, from_: int) -> list[Message]:
    order = desc(Message.id) if from_ < 0 else Message.id
    cmd = select(Message).where(Message.project_id == project_id).order_by(order).limit(abs(from_))
    return session.execute(cmd).scalars()


async def transmit(messages: list[Message], to_: User) -> list["MessageDTO"]:
    res = []
    for message in messages:
        message.transmit(to_)
        res.append(
            await MessageDTO.from_model_instance_async(message)
        )
    return res


UserDTO = dto_factory("UserDTO", User, exclude=["password", "roles", "projects", "messages", "recipient"])
ProjectDTO = dto_factory("ProjectDTO", Project, exclude=["messages", "members"])
MessageDTO = dto_factory(
    "MessageDTO",
    Message,
    exclude=["project", "sender", "recipients"],
    field_mapping={"id": ("id", int | None)}
)
