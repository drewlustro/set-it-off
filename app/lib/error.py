import logging.handlers
import datetime
# from hipchat.room import Room
# import hipchat.config
from app import config


# hipchat.config.token = config.HIPCHAT_TOKEN


# class _HipchatHandler(logging.Handler):
#     def emit(self, record, room_id=None, sender=None, color=None):
#         if not room_id:
#             room_id = config.HIPCHAT_ROOMID
#         if not sender:
#             sender = config.HIPCHAT_SENDER
#         if not color:
#             color = 'red'

#         try:
#             message = {'room_id': room_id,
#                        'from': sender,
#                        'notify': 1,
#                        'color': color,
#                        'message': record.message}
#             Room.message(**message)
#         except:  # swallow ALL errors here.
#             print "error"


# def get_mail_handler():
#     mail_handler = logging.handlers.SMTPHandler(
#         (config.INTERNAL_MAIL_SERVER, config.INTERNAL_MAIL_PORT),
#         config.ERROR_MAIL_SENDER_EMAIL,
#         [config.ERROR_MAIL_RECIPIENT_EMAIL],
#         'Stathub exception : %s' %
#         datetime.datetime.now().ctime(),
#         credentials=(config.INTERNAL_MAIL_USERNAME,
#                      config.INTERNAL_MAIL_PASSWORD))
#     mail_handler.setLevel(logging.ERROR)
#     mail_handler.setFormatter(logging.Formatter("""
# Time:               %(asctime)s

# %(message)s
# """))
#     return mail_handler


# def get_hipchat_handler():
#     hipchat_handler = _HipchatHandler()
#     hipchat_handler.setLevel(logging.ERROR)
#     hipchat_handler.setFormatter(logging.Formatter("""%(message)s"""))
#     return hipchat_handler


class StatHubError(Exception):
    pass
