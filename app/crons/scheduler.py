import time
import sys
import signal
import traceback
import logging
from apscheduler import events
from apscheduler.scheduler import Scheduler
from app import config
from app.lib import error
from app.lib.database import db

# ----------------------------------------------------------------------------
# Logger

_DEBUG_LOG_FORMAT = (
    '-' * 80 + '\n' +
    '%(levelname)s in %(module)s [%(pathname)s:%(lineno)d]:\n' +
    '%(message)s\n' +
    '-' * 80
)

logger = logging.getLogger(__name__)
del logger.handlers[:]

if config.DEBUG:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(_DEBUG_LOG_FORMAT))
    logger.addHandler(handler)

if config.FLASK_ENV == 'production':
    logger.addHandler(error.get_mail_handler())
    logger.addHandler(error.get_hipchat_handler())


# ----------------------------------------------------------------------------
# Event handlers

def shutdown_handler(signal, frame):
    print "%s captured -- shutting down" % signal
    sched.shutdown()
    sys.exit(0)

sched = Scheduler()
signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)


def event_handler(event):
    if event.exception:
        logger.error("SCHEDULER FAIL:\n%s\n%s\n%s" % (
            event.job, event.exception, traceback.format_exc()))
    else:
        logger.info("SUCCESS: %s" % event.job)

sched.add_listener(event_handler,
    events.EVENT_JOB_EXECUTED |
    events.EVENT_JOB_ERROR |
    events.EVENT_JOB_MISSED)


# ----------------------------------------------------------------------------
# Tasks

#sched.add_cron_job(send_digest, hour=11)

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    sched.start()
    sched.print_jobs()
    while True:
        time.sleep(10)
        db.remove()
