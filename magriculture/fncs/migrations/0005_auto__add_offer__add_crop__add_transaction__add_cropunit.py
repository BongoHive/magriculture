# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Offer'
        db.create_table('fncs_offer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('crop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.Crop'])),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.CropUnit'])),
            ('agent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.Agent'])),
            ('market', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.Market'])),
            ('marketmonitor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.MarketMonitor'])),
            ('price', self.gf('django.db.models.fields.FloatField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('fncs', ['Offer'])

        # Adding model 'Crop'
        db.create_table('fncs_crop', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('fncs', ['Crop'])

        # Adding M2M table for field units on 'Crop'
        db.create_table('fncs_crop_units', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('crop', models.ForeignKey(orm['fncs.crop'], null=False)),
            ('cropunit', models.ForeignKey(orm['fncs.cropunit'], null=False))
        ))
        db.create_unique('fncs_crop_units', ['crop_id', 'cropunit_id'])

        # Adding model 'Transaction'
        db.create_table('fncs_transaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('crop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.Crop'])),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.CropUnit'])),
            ('farmer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.Farmer'])),
            ('agent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.Agent'])),
            ('market', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.Market'])),
            ('amount', self.gf('django.db.models.fields.FloatField')()),
            ('price', self.gf('django.db.models.fields.FloatField')()),
            ('total', self.gf('django.db.models.fields.FloatField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('fncs', ['Transaction'])

        # Adding model 'CropUnit'
        db.create_table('fncs_cropunit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('fncs', ['CropUnit'])


    def backwards(self, orm):
        
        # Deleting model 'Offer'
        db.delete_table('fncs_offer')

        # Deleting model 'Crop'
        db.delete_table('fncs_crop')

        # Removing M2M table for field units on 'Crop'
        db.delete_table('fncs_crop_units')

        # Deleting model 'Transaction'
        db.delete_table('fncs_transaction')

        # Deleting model 'CropUnit'
        db.delete_table('fncs_cropunit')


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
        'fncs.crop': {
            'Meta': {'ordering': "['-name']", 'object_name': 'Crop'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'units': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['fncs.CropUnit']", 'symmetrical': 'False'})
        },
        'fncs.cropunit': {
            'Meta': {'ordering': "['-name']", 'object_name': 'CropUnit'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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
        'fncs.offer': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'Offer'},
            'agent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Agent']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'crop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Crop']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'market': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Market']"}),
            'marketmonitor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.MarketMonitor']"}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.CropUnit']"})
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
        'fncs.transaction': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'Transaction'},
            'agent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Agent']"}),
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'crop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Crop']"}),
            'farmer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Farmer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'market': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Market']"}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'total': ('django.db.models.fields.FloatField', [], {}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.CropUnit']"})
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
