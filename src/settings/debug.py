# -*- coding: utf-8 -* 
import logging.config
import os

web_autoreload = True

debug = True

LOGGING = {
    "version": 1,
    'disable_existing_loggers': False,
    "formatters": {
        "verbose": {"format": "%(levelname)-5s %(asctime)s %(filename)-12s:%(lineno)-3d-%(funcName)8s  ## %(message)s",
                    "datefmt": "%Y-%m-%dT%H:%M:%S,%03d",
                },
    },

    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },

    'loggers': {
        "handler_base":{
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
    
    'root': {
        "level": 'DEBUG',
        "handlers": ['console'],
    }
}

logging.config.dictConfig(LOGGING)
