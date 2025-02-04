from src.entities.mail.Email import Email


class ReceivedMail(Email):
    def __init__(self, sender, recipient, subject, body, message_id, id=None, received_at=None, read=False):
        super().__init__(id, sender, recipient, subject, body, received_at)
        self.message_id = message_id
        self.read = read