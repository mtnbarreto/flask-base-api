# project/api/devices.py

from project.api.common import exceptions

devices_blueprint = Blueprint('devices', __name__, template_folder='../templates/devices')


@devices_blueprint.route('/devices', methods=['POST'])
@authenticate
def add_apns_device(user_id):
    post_data = request.get_json()
    if not post_data:
        return exceptions.InvalidPayload()
    device_id   = post_data.get('device_id')
    device_type = post_data.get('device_type')
    pn_token    = post_data.get('pn_token')
    try:
        user = User.first_by(email=email)
        if not user:
            db.session.add(User(username=username, email=email, password=password))
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': f'{email} was added!'
            }
            return jsonify(response_object), 201
        else:
            response_object = {
                'status': 'error',
                'message': 'Sorry. That email already exists.'
            }
            return jsonify(response_object), 400
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        response_object = {
            'status': 'error',
            'message': 'Invalid payload.'
        }
        return jsonify(response_object), 400
