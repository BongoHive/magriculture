# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'FarmerGroup'
        db.create_table('fncs_farmergroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('zone', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.Zone'])),
            ('district', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.District'])),
        ))
        db.send_create_signal('fncs', ['FarmerGroup'])

        # Adding M2M table for field villages on 'FarmerGroup'
        db.create_table('fncs_farmergroup_villages', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('farmergroup', models.ForeignKey(orm['fncs.farmergroup'], null=False)),
            ('village', models.ForeignKey(orm['fncs.village'], null=False))
        ))
        db.create_unique('fncs_farmergroup_villages', ['farmergroup_id', 'village_id'])

        # Adding model 'Actor'
        db.create_table('fncs_actor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('farmergroup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.FarmerGroup'], null=True)),
        ))
        db.send_create_signal('fncs', ['Actor'])


    def backwards(self, orm):
        
        # Deleting model 'FarmerGroup'
        db.delete_table('fncs_farmergroup')

        # Removing M2M table for field villages on 'FarmerGroup'
        db.delete_table('fncs_farmergroup_villages')

        # Deleting model 'Actor'
        db.delete_table('fncs_actor')


    models = {
        'fncs.actor': {
            'Meta': {'ordering': "['-name']", 'object_name': 'Actor'},
            'farmergroup': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.FarmerGroup']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'fncs.district': {
            'Meta': {'ordering': "['-name']", 'object_name': 'District'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'rpiarea': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.RPIArea']"})
        },
        'fncs.farmergroup': {
            'Meta': {'ordering': "['-name']", 'object_name': 'FarmerGroup'},
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.District']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'villages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['fncs.Village']", 'symmetrical': 'False'}),
            'zone': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.Zone']"})
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
