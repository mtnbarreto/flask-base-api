# project/api/common/error_handlers.py

from flask import jsonify

def handle_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def handle_general_exception(error):
    response = jsonify({'status': 'error', 'message': 'Something went wrong!'})
    response.status_code = 500
    return response
