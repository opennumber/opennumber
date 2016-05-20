# deploy
# 为了保证supervisorctl这个命令在ubuntu用户下可用,请保证 supervisor.conf 文件里的unix 为 /tmp/supervisor.sock
#

SUPERVISORCTL=supervisorctl
OPENNUMBER_GROUP=opennumber
port=2000 2001 2002 2003


# 当前的服务器的运行状态
status:
	@for port in ${port}; do ${SUPERVISORCTL} status ${OPENNUMBER_GROUP}:$${port}; done

#
start:
	${SUPERVISORCTL} start ${OPENNUMBER_GROUP}:*

# 
stop:
	${SUPERVISORCTL} stop ${OPENNUMBER_GROUP}:*

# 
restart:
	${SUPERVISORCTL} restart ${OPENNUMBER_GROUP}:*


# 把当前的代码copy到开发服务器上, make copy_to_server target=username@host:/path
copy_to_production_server:
	find . -name '*.pyc' -delete
	find . -name '*.py~' -delete
	find . -name '*.pyo' -delete
	find . -name '*~' -delete
	scp -r * ubuntu@$(opennumber_production_server_path)

copy_to_debug_server:
	find . -name '*.pyc' -delete
	find . -name '*.py~' -delete
	find . -name '*.pyo' -delete
	find . -name '*~' -delete
	scp -r * ubuntu@$(opennumber_debug_server_path)

clean:
	find . -name '*~' -delete
	find . -name '*.pyc' -delete
	find . -name '*.py~' -delete
	find . -name '*.pyo' -delete
