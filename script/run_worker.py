import sys
import logging
from pyres.worker import Worker
from pyres.horde import Khan
from pyres import setup_logging
from app.lib import error
from app import config



def pyres_worker(queue, log_filename=None):
    """Start the pyres worker on the queue"""
    #setup_logging(log_level=logging.INFO, filename=log_filename)
    Worker.run([queue], server='%s:%d' % (config.REDIS_HOST, config.REDIS_PORT))


def pyres_manager(queue, pool_size, log_filename=None):
    #setup_logging(log_level=logging.INFO, filename=log_filename)
    Khan.run(pool_size=pool_size,
             queues=[queue],
             server='%s:%d' % (config.REDIS_HOST, config.REDIS_PORT),
             logging_level=logging.INFO,
             log_file=log_filename)

if __name__ == '__main__':
    #logger = logging.getLogger('pyres.worker')
    #logger.addHandler(error.get_mail_handler())
    #logger2 = logging.getLogger('pyres.manager')
    #logger2.addHandler(error.get_mail_handler())

    # hipchat logger; copy/paste from lookmark/__init__
    # hipchat_handler = HipchatHandler()
    # hipchat_handler.setLevel(logging.ERROR)
    # hipchat_handler.setFormatter(logging.Formatter("""%(message)s"""))

    # logger.addHandler(hipchat_handler)
    # logger2.addHandler(hipchat_handler)

    #try:
    #    pool_size = sys.argv[3]
    #except:
    #    pool_size = 5
    #pyres_manager(sys.argv[1], pool_size, sys.argv[2])
    try:
        logfile = sys.argv[2]
    except IndexError:
        logfile = None

    pyres_worker(sys.argv[1], logfile)
