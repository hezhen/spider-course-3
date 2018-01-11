# msg type, could be REGISTER, UNREGISTER and HEARTBEAT
MSG_TYPE	= 'TYPE'

# send register
REGISTER 	= 'REGISTER'

# unregister client with id assigned by master
UNREGISTER 	= 'UNREGISTER'

# send heart beat to server with id
HEARTBEAT	= 'HEARTBEAT'

# notify master paused with id
PAUSED 		= 'PAUSED'

# notify master resumed with id
RESUMED		= 'RESUMED'

# notify master resumed with id
SHUTDOWN		= 'SHUTDOWN'

# client id key word
CLIENT_ID 	= 'CLIENT_ID'

# server status key word
ACTION_REQUIRED	= 'ACTION_REQUIRED'

# server require pause
PAUSE_REQUIRED	= 'PAUSE_REQUIRED'

# server require pause
RESUME_REQUIRED	= 'RESUME_REQUIRED'

# server require shutdown
SHUTDOWN_REQUIRED	= 'SHUTDOWN_REQUIRED'

# server status key word
SERVER_STATUS	= 'SERVER_STATUS'

# server status values
STATUS_RUNNING	= 'STATUS_RUNNING'

STATUS_PAUSED 	= 'STATUS_PAUSED'

STATUS_SHUTDOWN	= 'STATUS_SHUTDOWN'

STATUS_CONNECTION_LOST	= 'STATUS_CONNECTION_LOST'

ERROR 	= 'ERROR'

# client id not found, then it needs to register itself
ERR_NOT_FOUND	= 'ERR_NOT_FOUND'