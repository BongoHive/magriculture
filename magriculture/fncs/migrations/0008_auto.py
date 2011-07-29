# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding M2M table for field crops on 'Farmer'
        db.create_table('fncs_farmer_crops', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('farmer', models.ForeignKey(orm['fncs.farmer'], null=False)),
            ('crop', models.ForeignKey(orm['fncs.crop'], null=False))
        ))
        db.create_unique('fncs_farmer_crops', ['farmer_id', 'crop_id'])


    def backwards(self, orm):
        
        # Removing M2M table for field crops on 'Farmer'
        db.delete_table('fncs_farmer_crops')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'fncs.actor': {
            'Meta': {'ordering': "['-name']", 'object_name': 'Actor'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
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
            'crops': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['fncs.Crop']", 'symmetrical': 'False'}),
            'farmergroup': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.FarmerGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markets': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['fncs.Market']", 'symmetrical': 'False'})
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
