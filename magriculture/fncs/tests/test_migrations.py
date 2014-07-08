from django.test import TransactionTestCase
from django.contrib.auth.models import User
from django.core.management import call_command
from south.migration import Migrations
from magriculture.fncs.tests import utils


# http://micknelson.wordpress.com/2013/03/01/testing-django-migrations/
class TestDuplicatesDataMigration(TransactionTestCase):
    """
    Testing to see if the migration removes and stores the duplicates.
    """
    start_migration = "0040_auto__del_field_farmergroup_agent__add_field_farmergroup_actor"
    dest_migration = "0041_delete_test_data_by_phonenumber_and_datecreated"
    django_application = "auth"

    def setUp(self):
        super(TestDuplicatesDataMigration, self).setUp()
        migrations = Migrations(self.django_application)
        self.start_orm = migrations[self.start_migration].orm()
        self.dest_orm = migrations[self.dest_migration].orm()

        # Ensure the migration history is up-to-date with a fake migration.
        # The other option would be to use the south setting for these tests
        # so that the migrations are used to setup the test db.
        call_command('migrate', self.django_application, fake=True,
                     verbosity=0)

        # Then migrate back to the start migration.
        call_command('migrate', self.django_application, self.start_migration,
                     verbosity=0)

    def tearDown(self):
        # Leave the db in the final state so that the test runner doesn't
        # error when truncating the database.
        call_command('migrate', self.django_application, verbosity=0)

    def migrate_to_dest(self):
        call_command('migrate', self.django_application, self.dest_migration,
                     verbosity=0)

    def test_migration(self):
        utils.create_farmer(msisdn='12345')
        utils.create_farmer(msisdn='22222')
        utils.create_farmer(msisdn='23333')
        utils.create_farmer(msisdn='33333')
        utils.create_farmer(msisdn='123.0')
        utils.create_farmer(msisdn='12341234.0')
        utils.create_farmer(msisdn='3563457337.0')
        utils.create_farmer(msisdn='123412346666666.0')
        self.migrate_to_dest()

