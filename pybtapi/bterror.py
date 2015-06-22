class BTError(object):
    ERR_UNKNOWN     = -1
    ERR_NO_CMD      = -2
    ERR_UNKN_CMD    = -3

    ERROR_MSG = {
        ERR_UNKNOWN:    "Unknown error",
        ERR_NO_CMD:     "No command given",
        ERR_UNKN_CMD:   "Unknown command"
    }

    @staticmethod
    def _send_error(handler, error = -1, error_message = ""):
        if len(error_message) < 1:
            error_message = BTError.ERROR_MSG[error]

        handler.send_error(error_code = error, error_message = error_message)