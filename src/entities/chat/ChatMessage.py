from datetime import datetime


class ChatMessage:
    def __init__(self, id=None, sender=None, message=None, timestamp=None):
        self.id = id
        self.sender = sender
        self.message = message
        self.timestamp = timestamp or datetime.now()

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, sender={self.sender}, message={self.message}, timestamp={self.timestamp})>"
