from flask_mail import Mail, Message

class EmailUtils:
    def __init__(self, app):
        self.app = app
        self.app.config['MAIL_SERVER'] = 'smtp.gmail.com'
        self.app.config['MAIL_PORT'] = 587
        self.app.config['MAIL_USE_TLS'] = True
        self.app.config['MAIL_USERNAME'] = 'info@orangecatcycles.com'  # Your Google Workspace email
        self.app.config['MAIL_PASSWORD'] = 'kkqz owcg sxgi hdsx'  # Your generated app password
        self.mail = Mail(self.app)

    def sendMail(self, subject, body, recipient):
        try:
            sender = 'info@orangecatcycles.com'
            msg = Message(subject,
                            sender=sender,
                            recipients=[recipient])
            msg.body = body
            self.mail.send(msg)
            return True
        except Exception as e:
            print(e)
            return False