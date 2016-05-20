# -*- coding: utf-8 -*
'''
为了保证账户的安全，所有的数据库和redis等用户密码信息不能存放在代码仓库中。可通过以下方法进行配置：
mkdir target_dir                # 创建用于存放账户信息的目录
export PYTHONPATH=target_dir:$PYTHONPATH # 导入到python path
cp repo/src/env_template.py target_dir/opennumber_env_debug.py # 创建debug模块，
cp repo/src/env_template.py target_dir/opennumber_env_production.py # 创建production模块
vim target_dir/opennumber_env_debug.py # 修改对应的信息
export opennumber_runmode=debug; #设置runmode opennumber_runmode=production

python repo/src/main.py
'''
import os
import logging
import sys
from .base import *


runmode = os.getenv("opennumber_runmode", "debug").strip()


assert runmode in runmode_list, "invalid runmode: %s, choice from %s" % (runmode, runmode_list)

# load settings
if runmode == "debug":
    from .debug import *

elif runmode == "production":
    from .production import *

else:
    pass


# load env

help = sys.modules[__name__].__doc__
try:
    if runmode == "debug":
        from opennumber_env_debug import *

    elif runmode == "production":
        from opennumber_env_production import *

    else:
        pass

except ImportError as e:
    module_name = 'opennumber_env_%s' % (runmode)
    logging.exception("import module '%s' error: \n%s", module_name, help)
    raise

logging.warn("load settings from %s. export opennumber_runmode=%s", runmode, runmode)

