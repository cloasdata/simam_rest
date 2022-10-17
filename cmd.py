import argparse
import time
from pathlib import Path

from client import Client
from tui import App
from src.simam.database.install import install_db
from src.simam.config.config import config, DEFAULT_CONFIG_INI

parser = argparse.ArgumentParser("Tiny Client. Communicates with the given project channel.")
parser.add_argument('-c', '--credentials', nargs=3, help="Credentials: Server,login,password")
parser.add_argument("-t", "--tui", type=str, nargs=1, help="Must provide project id")
parser.add_argument("--send", type=str, nargs=2, help="Must provide a project id and text to send.")
parser.add_argument("--fetch", type=int, nargs=1)
parser.add_argument("--listen", type=int, nargs=1)


def main(args):
    server, login_name, password = args.credentials
    client = Client(server)
    client.do_auth(login_name, password)

    if args.tui:
        app = App(client, args.tui[0])
        app.run()
    elif args.fetch:
        messages = client.fetch_all_messages(project_id=args.fetch[0])
        [pretty_print(client, msg) for msg in messages]
    elif args.send:
        client.send_message(project_id=args.send[0],
                            msg=args.send[1]
                            )
    elif args.listen:
        try:
            messages = client.fetch_all_messages(args.listen[0])
            [pretty_print(client, msg) for msg in messages]
            while True:
                time.sleep(1)
                message = client.get_message(args.listen[0])
                if message:
                    pretty_print(client, message)
        except KeyboardInterrupt:
            print("Bye!")
    else:
        return


parser.set_defaults(func=main)

sp = parser.add_subparsers(title="Install a demo database")
parser_database = sp.add_parser("database")
parser_database.add_argument("--install", type=str, nargs=1)


def database(args):
    config["database"]["path"] = str(Path(args.install[0]))
    config.write(DEFAULT_CONFIG_INI.open("w"))
    install_db()


parser_database.set_defaults(func=database)


def pretty_print(client: Client, message):
    user = client.get_user(message.sender_id)
    project = client.get_project(message.project_id)
    txt = f"{user.name}->{project.name}@{message.issue_date}:\n\t\t'{message.message_text}'\n"
    print(txt)


if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)
