import datetime
from pathlib import Path

from src.simam.config.config import config
from src.simam.database.engine import engine
from src.simam.database.session import new_session
from simam.model.model import Permission, Role, User, Project, Message
from src.simam.util.hashing import hash_password
from src.simam.model.model import Base

session = new_session()


def install_db():
    db_path = Path(config["database"]["path"])
    if db_path.exists():
        db_path.unlink(missing_ok=True)
    create_all()
    add_permissions()
    add_roles()
    admin = add_admin_user()
    prj = create_start_project()
    users = add_example_user()
    for user in users + [admin,]:
        user.projects.append(prj)
    session.commit()
    add_starting_message(admin, prj)
    session.commit()


def create_start_project():
    prj =  Project(name="start_project", short_name="strt_prjct", costcenter="111111")
    session.add(prj)
    return prj

def create_all():
    Base.metadata.create_all(engine)


def add_permissions():
    for perm in ["post_message"]:
        session.add(
            Permission(name=perm)
        )


def add_roles():
    post_message = session.query(Permission).where(Permission.name == "post_message").one()
    for role in ["admin", "user", "moderator"]:
        role = Role(name=role)
        role.permissions.append(post_message)
        session.add(role)
    session.commit()



def add_admin_user():
    admin = User(
        first_name="seimen",
        name="baua",
        login_name="admin",
        email="seimen@cloasdata.de",
        password=hash_password("admin")
    )
    admin_role: Role = session.query(Role).where(Role.name == "admin").one()
    admin.roles.append(admin_role)
    session.add(admin)
    return admin


def add_example_user():
    role: Role = session.query(Role).where(Role.name == "user").one()
    res = []
    for idx in range(3):
        user = User(
            first_name=f"user_{idx}",
            name=f"user_{idx}",
            login_name=f"user_{idx}",
            email=f"user_{idx}@hans.de",
            password=hash_password(f"user_{idx}"))
        user.roles.append(role)
        session.add(user)
        res.append(user)
    return res


def add_starting_message(user: User, project: Project):
    for txt in [
        f"server installed - {datetime.datetime.now()}",
        "Welcome to simam_rest\nhave fun",
        "don't do anything stupid",
        "no",
        "yes",
        "More message to come...... Even longer ones..... "
        "Just to see if text wrapping works as expected. Does it? Yes? Maybe?"
        "Needs to be a very long message... to see if it is working right."

    ]:
        msg = Message(message_text=txt, sender=user)
        msg.project = project
        msg.send_to_project_members()
        session.add(msg)


if __name__ == "__main__":
    install_db()
