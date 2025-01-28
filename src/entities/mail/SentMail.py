from src.entities.mail.Email import Email


class SentMail(Email):
    def __init__(self, sender, recipient, subject, body, attachment_path=None, id=None, sent_at=None):
        super().__init__(id, sender, recipient, subject, body, sent_at)
        self.attachment_path = attachment_path
