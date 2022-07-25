from flask_mail import Message
from app import mail

def test_reset_password_email(new_user, test_client):
    with mail.record_messages() as outbox:

        mail.send_message(subject='testing',
                        body='test',
                        recipients="mw2056@bath.ac.uk")

        assert len(outbox) == 1
        assert outbox[0].subject == "testing"