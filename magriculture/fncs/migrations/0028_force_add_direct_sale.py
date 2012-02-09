# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DirectSale'
        db.create_table('fncs_directsale', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('transaction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.Transaction'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('fncs', ['DirectSale'])

    def backwards(self, orm):
        # Deleting model 'DirectSale'
        db.delete_table('fncs_directsale')


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
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
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
            'Meta': {'ordering': "['name']", 'object_name': 'Crop'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'units': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['fncs.CropUnit']", 'symmetrical': 'False'})
        },
        'fncs.cropreceipt': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'CropReceipt'},
            'agent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Agent']"}),
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'crop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Crop']"}),
            'farmer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Farmer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'market': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Market']"}),
            'quality': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'reconciled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.CropUnit']"})
        },
        'fncs.cropunit': {
            'Meta': {'ordering': "['-name']", 'object_name': 'CropUnit'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'fncs.district': {
            'Meta': {'ordering': "['-name']", 'object_name': 'District'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'province': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Province']"})
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
            'farmergroup': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.FarmerGroup']", 'null': 'True'}),
            'hh_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markets': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['fncs.Market']", 'symmetrical': 'False'}),
            'number_of_females': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'number_of_males': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'participant_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'wards': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['fncs.Ward']", 'symmetrical': 'False'})
        },
        'fncs.farmergroup': {
            'Meta': {'ordering': "['-name']", 'object_name': 'FarmerGroup'},
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.District']", 'null': 'True'}),
            'extensionofficer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.ExtensionOfficer']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'wards': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['fncs.Ward']", 'symmetrical': 'False'}),
            'zone': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Zone']", 'null': 'True'})
        },
        'fncs.groupmessage': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'GroupMessage'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'farmergroups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['fncs.FarmerGroup']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Actor']"})
        },
        'fncs.market': {
            'Meta': {'ordering': "['name']", 'object_name': 'Market'},
            'altitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.District']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'volume': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '100', 'blank': 'True'})
        },
        'fncs.marketmonitor': {
            'Meta': {'object_name': 'MarketMonitor'},
            'actor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Actor']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markets': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['fncs.Market']", 'symmetrical': 'False'}),
            'rpiareas': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['fncs.RPIArea']", 'symmetrical': 'False'})
        },
        'fncs.message': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'Message'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.GroupMessage']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'receivedmessages_set'", 'to': "orm['fncs.Actor']"}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sentmessages_set'", 'to': "orm['fncs.Actor']"})
        },
        'fncs.note': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'Note'},
            'about_actor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachednote_set'", 'to': "orm['fncs.Actor']"}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Actor']"})
        },
        'fncs.offer': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'Offer'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'crop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Crop']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'market': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Market']"}),
            'marketmonitor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.MarketMonitor']"}),
            'price_ceiling': ('django.db.models.fields.FloatField', [], {}),
            'price_floor': ('django.db.models.fields.FloatField', [], {}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.CropUnit']"})
        },
        'fncs.province': {
            'Meta': {'ordering': "['-name']", 'object_name': 'Province'},
            'code': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'default': "'--'", 'max_length': '100'}),
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
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'crop_receipt': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.CropReceipt']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'total': ('django.db.models.fields.FloatField', [], {})
        },
        'fncs.ward': {
            'Meta': {'ordering': "['-name']", 'object_name': 'Ward'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
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
