# -*- coding: utf-8 -*
import os
import logging
import settings

opennumber_env = os.getenv("opennumber_env", "debug")
assert opennumber_settings in settings_list, "invalid env variable: %s, choice from %s" % (opennumber_settings, settings.settings_list)

if opennumber_env == "debug":
    from opennumber_debug import *
elif opennumber_env == "production":
    from opennumber_production import *
else:
    pass

logging.warn("load env from %s", opennumber_env)


