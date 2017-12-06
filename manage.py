# manage.py

import unittest
import coverage

from flask_script import Manager
from flask_migrate import MigrateCommand

from project import app, db
from project.models.models import User, EventDescriptor, Group, UserGroupAssociation

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
def routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, rule))
        output.append(line)

    for line in sorted(output):
        print(line)


@manager.command
def recreate_db():
    """Recreates a database."""
    db.drop_all()
    db.create_all()
    db.session.commit()


@manager.command
def seed_db():
    """Seeds the database."""
    eventDesc = EventDescriptor(id=1, name="Seed Events Name", description="Seed db Event from {1}")
    db.session.add(eventDesc)
    group = Group(name="Group Name")
    db.session.add(group)
    user1 = User(username='martin', email="mtn.barreto@gmail.com", password="password", cellphone_number="98983510", cellphone_cc="+598")
    user2 = User(username='barreto', email="barretomartin1984@gmail.com", password="password")
    user3 = User(username='cheluskis', email="marcerossi21@gmail.com", password="password")
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    user_group_association1 = UserGroupAssociation(user=user1, group=group)
    db.session.add(user_group_association1)
    user_group_association2 = UserGroupAssociation(user=user2, group=group)
    db.session.add(user_group_association2)
    user_group_association3 = UserGroupAssociation(user=user3, group=group)
    db.session.add(user_group_association3)
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


if __name__ == '__main__':
    manager.run()
