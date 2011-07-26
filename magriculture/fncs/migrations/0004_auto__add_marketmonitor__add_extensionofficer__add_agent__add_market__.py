# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MarketMonitor'
        db.create_table('fncs_marketmonitor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.Actor'])),
        ))
        db.send_create_signal('fncs', ['MarketMonitor'])

        # Adding M2M table for field markets on 'MarketMonitor'
        db.create_table('fncs_marketmonitor_markets', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('marketmonitor', models.ForeignKey(orm['fncs.marketmonitor'], null=False)),
            ('market', models.ForeignKey(orm['fncs.market'], null=False))
        ))
        db.create_unique('fncs_marketmonitor_markets', ['marketmonitor_id', 'market_id'])

        # Adding M2M table for field rpiareas on 'MarketMonitor'
        db.create_table('fncs_marketmonitor_rpiareas', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('marketmonitor', models.ForeignKey(orm['fncs.marketmonitor'], null=False)),
            ('rpiarea', models.ForeignKey(orm['fncs.rpiarea'], null=False))
        ))
        db.create_unique('fncs_marketmonitor_rpiareas', ['marketmonitor_id', 'rpiarea_id'])

        # Adding model 'ExtensionOfficer'
        db.create_table('fncs_extensionofficer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.Actor'])),
        ))
        db.send_create_signal('fncs', ['ExtensionOfficer'])

        # Adding model 'Agent'
        db.create_table('fncs_agent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.Actor'])),
        ))
        db.send_create_signal('fncs', ['Agent'])

        # Adding M2M table for field farmers on 'Agent'
        db.create_table('fncs_agent_farmers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('agent', models.ForeignKey(orm['fncs.agent'], null=False)),
            ('farmer', models.ForeignKey(orm['fncs.farmer'], null=False))
        ))
        db.create_unique('fncs_agent_farmers', ['agent_id', 'farmer_id'])

        # Adding M2M table for field markets on 'Agent'
        db.create_table('fncs_agent_markets', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('agent', models.ForeignKey(orm['fncs.agent'], null=False)),
            ('market', models.ForeignKey(orm['fncs.market'], null=False))
        ))
        db.create_unique('fncs_agent_markets', ['agent_id', 'market_id'])

        # Adding model 'Market'
        db.create_table('fncs_market', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('district', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.District'])),
        ))
        db.send_create_signal('fncs', ['Market'])

        # Adding model 'Farmer'
        db.create_table('fncs_farmer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.Actor'])),
            ('farmergroup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.FarmerGroup'])),
        ))
        db.send_create_signal('fncs', ['Farmer'])

        # Adding M2M table for field agents on 'Farmer'
        db.create_table('fncs_farmer_agents', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('farmer', models.ForeignKey(orm['fncs.farmer'], null=False)),
            ('agent', models.ForeignKey(orm['fncs.agent'], null=False))
        ))
        db.create_unique('fncs_farmer_agents', ['farmer_id', 'agent_id'])

        # Adding field 'FarmerGroup.extensionofficer'
        db.add_column('fncs_farmergroup', 'extensionofficer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.ExtensionOfficer'], null=True), keep_default=False)

        # Deleting field 'Actor.farmergroup'
        db.delete_column('fncs_actor', 'farmergroup_id')


    def backwards(self, orm):
        
        # Deleting model 'MarketMonitor'
        db.delete_table('fncs_marketmonitor')

        # Removing M2M table for field markets on 'MarketMonitor'
        db.delete_table('fncs_marketmonitor_markets')

        # Removing M2M table for field rpiareas on 'MarketMonitor'
        db.delete_table('fncs_marketmonitor_rpiareas')

        # Deleting model 'ExtensionOfficer'
        db.delete_table('fncs_extensionofficer')

        # Deleting model 'Agent'
        db.delete_table('fncs_agent')

        # Removing M2M table for field farmers on 'Agent'
        db.delete_table('fncs_agent_farmers')

        # Removing M2M table for field markets on 'Agent'
        db.delete_table('fncs_agent_markets')

        # Deleting model 'Market'
        db.delete_table('fncs_market')

        # Deleting model 'Farmer'
        db.delete_table('fncs_farmer')

        # Removing M2M table for field agents on 'Farmer'
        db.delete_table('fncs_farmer_agents')

        # Deleting field 'FarmerGroup.extensionofficer'
        db.delete_column('fncs_farmergroup', 'extensionofficer_id')

        # Adding field 'Actor.farmergroup'
        db.add_column('fncs_actor', 'farmergroup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.FarmerGroup'], null=True), keep_default=False)


    models = {
        'fncs.actor': {
            'Meta': {'ordering': "['-name']", 'object_name': 'Actor'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'fncs.agent': {
            'Meta': {'object_name': 'Agent'},
            'actor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Actor']"}),
            'farmers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['fncs.Farmer']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markets': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['fncs.Market']", 'symmetrical': 'False'})
        },
        'fncs.district': {
            'Meta': {'ordering': "['-name']", 'object_name': 'District'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'rpiarea': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.RPIArea']"})
        },
        'fncs.extensionofficer': {
            'Meta': {'object_name': 'ExtensionOfficer'},
            'actor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Actor']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'fncs.farmer': {
            'Meta': {'object_name': 'Farmer'},
            'actor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Actor']"}),
            'agents': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['fncs.Agent']", 'symmetrical': 'False'}),
            'farmergroup': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.FarmerGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'fncs.farmergroup': {
            'Meta': {'ordering': "['-name']", 'object_name': 'FarmerGroup'},
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.District']"}),
            'extensionofficer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.ExtensionOfficer']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'villages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['fncs.Village']", 'symmetrical': 'False'}),
            'zone': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Zone']"})
        },
        'fncs.market': {
            'Meta': {'ordering': "['-name']", 'object_name': 'Market'},
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.District']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'fncs.marketmonitor': {
            'Meta': {'object_name': 'MarketMonitor'},
            'actor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Actor']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markets': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['fncs.Market']", 'symmetrical': 'False'}),
            'rpiareas': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['fncs.RPIArea']", 'symmetrical': 'False'})
        },
        'fncs.province': {
            'Meta': {'ordering': "['-name']", 'object_name': 'Province'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'fncs.rpiarea': {
            'Meta': {'ordering': "['-name']", 'object_name': 'RPIArea'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'provinces': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['fncs.Province']", 'symmetrical': 'False'})
        },
        'fncs.village': {
            'Meta': {'ordering': "['-name']", 'object_name': 'Village'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ward': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Ward']"})
        },
        'fncs.ward': {
            'Meta': {'ordering': "['-name']", 'object_name': 'Ward'},
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.District']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'fncs.zone': {
            'Meta': {'ordering': "['-name']", 'object_name': 'Zone'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'rpiarea': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.RPIArea']"})
        }
    }

    complete_apps = ['fncs']
