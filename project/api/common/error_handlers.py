from flask import jsonify

def handle_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response



# InvalidUsage
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
