# from app import celery
# from flask_mail import Mail, Message
# import os

# class EmailUtils:
#     def __init__(self, app):
#         self.app = app
#         self.app.config['MAIL_SERVER'] = 'smtp.gmail.com'
#         self.app.config['MAIL_PORT'] = 587
#         self.app.config['MAIL_USE_TLS'] = True
#         self.app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'info@orangecatcycles.com')
#         self.app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
#         self.mail = Mail(self.app)

#     @celery.task(name='app.send_email_task')
#     def send_email_task(self, subject, sender, recipients, body):
#         try:
#             print('Sending email')
#             msg = Message(subject, sender=sender, recipients=recipients)
#             msg.body = body
#             self.mail.send(msg)
#             print('Email sent')
#             return True
#         except Exception as e:
#             print(e)
#             return False
            