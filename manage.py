# manage.py

import unittest
import coverage
import urllib.parse

from flask.cli import FlaskGroup

from project import app, db
from project.models.user import User
from project.models.event_descriptor import EventDescriptor
from project.models.group import Group
from project.models.user_group_association import UserGroupAssociation

cli = FlaskGroup(app)

COV = coverage.coverage(
    branch=True,
    include='project/*',
    omit=[
        'project/static/*'
    ]
)
COV.start()

@cli.command()
def test():
    """Runs the tests without code coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test_*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

@cli.command('recreate_db')
def recreate_db():
    """Recreates a database."""
    db.reflect()
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command('seed_db')
def seed_db():
    """Seeds the database."""
    event_desc = EventDescriptor(id=1, name="Seed Events Name", description="Seed db Event from {1}")
    db.session.add(event_desc)
    group = Group(name="Group Name")
    db.session.add(group)
    user1 = User(username='martin', email="a@a.com", password="password", cellphone_number="98983510", cellphone_cc="+598")
    user2 = User(username='barreto', email="b@b.com", password="password")
    user3 = User(username='cheluskis', email="c@c.com", password="password")
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


@cli.command()
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover('tests')
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
    cli()
