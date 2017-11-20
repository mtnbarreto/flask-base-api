# manage.py

import unittest
import coverage

from flask_script import Manager
from flask_migrate import MigrateCommand

from project import app, db, celery
from project.models.models import User

COV = coverage.coverage(
    branch=True,
    include='project/*',
    omit=[
        'project/static/*'
    ]
)
COV.start()

manager = Manager(app)
manager.add_command('db', MigrateCommand)

@manager.command
def test():
    """Runs the tests without code coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test_*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

@manager.command
def recreate_db():
    """Recreates a database."""
    db.drop_all()
    db.create_all()
    db.session.commit()

@manager.command
def seed_db():
    """Seeds the database."""
    db.session.add(User(username='martin', email="mtn.barreto@gmail.com", password="password", cell_phone_number="+59898983510"))
    db.session.add(User(username='barreto', email="barretomartin1984@gmail.com", password="password"))
    db.session.commit()

@manager.command
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover('project/tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        COV.html_report()
        COV.erase()
        return 0
    return 1


from project.utils.twilio import send_account_verification_code

@manager.command
def send_test_sms():
    """Send test sms with envoronment configuration."""
    user = db.session.query(User).filter(User.username == 'martin').first()
    send_account_verification_code(user = user)

if __name__ == '__main__':
    manager.run()
