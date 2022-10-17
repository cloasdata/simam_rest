import collections
import queue
import threading
import time
from queue import Queue
import textwrap

from asciimatics.screen import ManagedScreen
from asciimatics.event import KeyboardEvent

from client import Client
from src.simam.model.model import MessageDTO


def receiver(project_id: str, client: Client, queue: Queue):
    messages = client.fetch_all_messages(project_id=project_id)
    [queue.put(msg) for msg in messages]
    while True:
        time.sleep(1)
        message = client.get_message(project_id=project_id)
        if message:
            queue.put_nowait(message)


def sender(client: Client, queue: Queue):
    while True:
        project_id, message = queue.get()
        client.send_message(project_id=project_id, msg=message)


class App:
    def __init__(self, client: Client, project_id="1"):
        self.client = client
        self.project_id = project_id
        self.message_queue = Queue()
        self.sender_queue = Queue()
        self.receiver_thread = threading.Thread(
            target=receiver,
            args=(project_id, client, self.message_queue),
            name="Receiver",
            daemon=True
        )
        self.receiver_thread.start()
        self.sender_thread = threading.Thread(
            target=sender,
            args=(client, self.sender_queue),
            name="Sender",
            daemon=True,
        )
        self.sender_thread.start()
        self.message_buffer = collections.deque()
        self._key_buffer = ""
        self._echo_line = 8
        self._line_index = 0
        self._line_buffer: list[str] = []
        self._run = True

    def run(self):
        with ManagedScreen() as self.screen:
            while self._run:
                self.handle_messages()
                self.screen.print_at("Tiny Client 0.1", 0, 0, colour=3)
                self.screen.print_at(self.client.user.login_name, 20, 0, colour=5)
                self._update_line_buffer()
                self.handle_events()
                self.screen.print_at(
                    "Enter Message and press Enter. To Scroll use Up, Down or Page Down. ctrl-q to quit",
                    0,
                    self.screen.height - 2,
                    colour=4,

                )
                self.screen.print_at(self._key_buffer, 0, self.screen.height - 1)
                self.screen.move(len(self._key_buffer), self.screen.height - 1)
                time.sleep(0.01)
                self.screen.refresh()
            else:
                self.screen.clear()
                self.screen.print_at("Leaving.Bye.", self.screen.width//2, self.screen.height//2, colour=3)
                self.screen.refresh()
                time.sleep(1)

    def handle_messages(self):
        try:
            msg = self.message_queue.get_nowait()
            self.message_buffer.append(msg)
            self._scroll_last()
        except queue.Empty:
            return

    def _update_line_buffer(self):
        while self.message_buffer:
            lines = self.display_as_text(self.message_buffer.popleft(), 100)
            self._line_buffer.extend(lines)

    def draw_messages(self):
        screen_size = self.screen.height - 4
        lines = self._line_buffer[self._line_index:self._line_index + screen_size]
        for index, line in enumerate(lines):
            self.screen.print_at(
                line + " " * (self.screen.width - len(line)),
                0,
                index + 1
            )

    def display_as_text(self, message: MessageDTO, line_width: int = 100, indent: int = 4) -> list[str]:
        lines = []
        header = f"{message.issue_date} - {self.client.get_user(message.sender_id).login_name} -> {self.client.get_project(message.project_id).name}:"
        lines.append(header)
        indent_lines = textwrap.wrap(message.message_text, line_width, initial_indent="   ", subsequent_indent="    ")
        lines.extend(indent_lines)
        return lines

    def handle_events(self):
        event = self.screen.get_event()
        if isinstance(event, KeyboardEvent):
            self.screen.print_at(str(event.key_code) + "    ", 0, self.screen.height - 4)
            # self.screen.print_at(type(event.key_code),0,4)
            if event.key_code <= 31:
                if event.key_code == -300:  # backspace
                    self.screen.print_at("  ", len(self._key_buffer) - 1, self.screen.height - 1)
                    self._key_buffer = self._key_buffer[:-1]
                elif event.key_code == -204:  # cursor up
                    self._scroll_up()
                elif event.key_code == -206:  # cursor down
                    self._scroll_down()
                elif event.key_code == -208:  # page down
                    self._scroll_last()
                elif event.key_code == 17: # q
                    self._run = False
                elif event.key_code == 13:
                    self._enter()
            else:
                self._key_buffer += chr(event.key_code)

    def _enter(self):
        if self._key_buffer:
            self.sender_queue.put_nowait((self.project_id, self._key_buffer))
            self._key_buffer = ""
            self.screen.print_at(" " * self.screen.width, 0, self.screen.height - 1)

    def _scroll_up(self):
        if self._line_index > 1:
            self._line_index -= 1
            self._update_line_buffer()
            self.draw_messages()

    def _scroll_down(self):
        if self._line_index < len(self._line_buffer) - self.screen.height + 4:
            self._line_index += 1
            self._update_line_buffer()
            self.draw_messages()

    def _scroll_last(self):
        self._update_line_buffer()
        self._line_index = len(self._line_buffer) - self.screen.height + 4
        self.draw_messages()

