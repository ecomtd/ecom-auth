import sys
import logging
import uvicorn
import app.settings as settings


if __name__ == '__main__':
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s:\t%(message)s')
    handler.setFormatter(formatter)
    for logger in [logging.getLogger(name) for name in logging.root.manager.loggerDict]:
        logger.setLevel(logging.DEBUG)
        logger.handlers.clear()
        logger.addHandler(handler)
    uvicorn.run("app.main:app",
                host=settings.api_local_ip_address,
                port=settings.api_local_ip_port,
                log_level=settings.logging_level,
                workers=settings.workers_count)
