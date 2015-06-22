from bluetooth import *
import logging, asyncore, json

from .bterror import BTError

logger = logging.getLogger(__name__)

class BTHandler(asyncore.dispatcher_with_send):
    def __init__(self, socket, server):
        asyncore.dispatcher_with_send.__init__(self, socket)
        self._server = server
        self._data = ""

    def handle_read(self):
        try:
            data = self.recv(1024)
            if not data:
                return

            zero_char_index = data.find(chr(0))
            if zero_char_index == -1:
                # no 0-char in data - so we append all
                self._data += data
            else:
                # we have a 0-char in data - so append rest and handle
                self._data += data[:zero_char_index]
                self._handle_json()
        except IOError:
            pass

    def handle_close(self):
        while self.writeable():
            self.handle_write()
        self.close()

    def send_error(self, error_code, error_message):
        json_string = json.dumps({"error": error_code, "error_message": error_message, "success": False})
        self.send(json_string + chr(0))

    def send_success(self, data):
        json_string = json.dumps({"success": True, "data": data})
        self.send(json_string + chr(0))
    
    def _handle_json(self):
        if len(self._data) < 1:
            return

        try:
            json_object = json.loads(self._data)
            self._server.handle_command(handler = self, data = json_object)
        except Exception as e:
            BTError._send_error(handler = self, error = BTError.ERR_UNKNOWN, error_message = repr(e))

        self._data = ""