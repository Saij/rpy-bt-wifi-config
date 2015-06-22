from bluetooth import *
import logging
import asyncore

from .bthandler import BTHandler
from .bterror import BTError

logger = logging.getLogger(__name__)

class BTServer(asyncore.dispatcher):
    def __init__(self, uuid, service_name, port = PORT_ANY):
        asyncore.dispatcher.__init__(self)

        self._cmds = {}

        if not is_valid_uuid(uuid):
            raise ValueError("uuid %s is not valid" % uuid)

        self.port = port
        self.uuid = uuid
        self.service_name = service_name

        # Create BT Socket
        self.set_socket(BluetoothSocket(RFCOMM))
        self.bind(("", port))
        self.listen(1)
        advertise_service(self.socket, service_name, service_id = uuid, service_classes = [uuid, SERIAL_PORT_CLASS], profiles = [SERIAL_PORT_PROFILE])

        port = self.socket.getsockname()[1]

        logger.info("Waiting for connection on RFCOMM channel %d" % port)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            logger.debug("Incoming connection from %s" % repr(addr[0]))
            handler = BTHandler(socket = sock, server = self)

    def handle_command(self, handler, data):
        if "cmd" not in data:
            BTError._send_error(handler = handler, error = BTError.ERR_NO_CMD)
            return

        if data["cmd"] not in self._cmds:
            BTError._send_error(handler = handler, error = BTError.ERR_UNKN_CMD)
            return

        params = {}
        if "data" in data:
            params = data["data"]

        self._cmds[data["cmd"]](handler, **params)

    def add_command(self, command, function):
        self._cmds[command] = function