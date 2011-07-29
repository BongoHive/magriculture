# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Ward'
        db.create_table('fncs_ward', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('district', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.District'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('fncs', ['Ward'])

        # Adding model 'RPIArea'
        db.create_table('fncs_rpiarea', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('fncs', ['RPIArea'])

        # Adding M2M table for field provinces on 'RPIArea'
        db.create_table('fncs_rpiarea_provinces', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('rpiarea', models.ForeignKey(orm['fncs.rpiarea'], null=False)),
            ('province', models.ForeignKey(orm['fncs.province'], null=False))
        ))
        db.create_unique('fncs_rpiarea_provinces', ['rpiarea_id', 'province_id'])

        # Adding model 'Village'
        db.create_table('fncs_village', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ward', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.Ward'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('fncs', ['Village'])

        # Adding model 'Province'
        db.create_table('fncs_province', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('fncs', ['Province'])

        # Adding model 'District'
        db.create_table('fncs_district', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rpiarea', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.RPIArea'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('fncs', ['District'])

        # Adding model 'Zone'
        db.create_table('fncs_zone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rpiarea', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fncs.RPIArea'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('fncs', ['Zone'])


    def backwards(self, orm):
        
        # Deleting model 'Ward'
        db.delete_table('fncs_ward')

        # Deleting model 'RPIArea'
        db.delete_table('fncs_rpiarea')

        # Removing M2M table for field provinces on 'RPIArea'
        db.delete_table('fncs_rpiarea_provinces')

        # Deleting model 'Village'
        db.delete_table('fncs_village')

        # Deleting model 'Province'
        db.delete_table('fncs_province')

        # Deleting model 'District'
        db.delete_table('fncs_district')

        # Deleting model 'Zone'
        db.delete_table('fncs_zone')


    models = {
        'fncs.district': {
            'Meta': {'ordering': "['-name']", 'object_name': 'District'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'rpiarea': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fncs.RPIArea']"})
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
