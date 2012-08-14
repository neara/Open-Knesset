# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'GovLegislationCommitteeDecision'
        db.create_table('laws_govlegislationcommitteedecision', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('subtitle', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('source_url', self.gf('django.db.models.fields.URLField')(max_length=1024, null=True, blank=True)),
            ('bill', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='gov_decisions', null=True, to=orm['laws.Bill'])),
            ('stand', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('laws', ['GovLegislationCommitteeDecision'])

        # Adding model 'GovProposal'
        db.create_table('laws_govproposal', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('knesset_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('law', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='laws_govproposal_related', null=True, to=orm['laws.Law'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('source_url', self.gf('django.db.models.fields.URLField')(max_length=1024, null=True, blank=True)),
            ('booklet_number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('bill', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='gov_proposal', unique=True, null=True, to=orm['laws.Bill'])),
        ))
        db.send_create_signal('laws', ['GovProposal'])

        # Adding M2M table for field committee_meetings on 'GovProposal'
        db.create_table('laws_govproposal_committee_meetings', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('govproposal', models.ForeignKey(orm['laws.govproposal'], null=False)),
            ('committeemeeting', models.ForeignKey(orm['committees.committeemeeting'], null=False))
        ))
        db.create_unique('laws_govproposal_committee_meetings', ['govproposal_id', 'committeemeeting_id'])

        # Adding M2M table for field votes on 'GovProposal'
        db.create_table('laws_govproposal_votes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('govproposal', models.ForeignKey(orm['laws.govproposal'], null=False)),
            ('vote', models.ForeignKey(orm['laws.vote'], null=False))
        ))
        db.create_unique('laws_govproposal_votes', ['govproposal_id', 'vote_id'])


    def backwards(self, orm):
        
        # Deleting model 'GovLegislationCommitteeDecision'
        db.delete_table('laws_govlegislationcommitteedecision')

        # Deleting model 'GovProposal'
        db.delete_table('laws_govproposal')

        # Removing M2M table for field committee_meetings on 'GovProposal'
        db.delete_table('laws_govproposal_committee_meetings')

        # Removing M2M table for field votes on 'GovProposal'
        db.delete_table('laws_govproposal_votes')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'committees.committee': {
            'Meta': {'object_name': 'Committee'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'committees'", 'symmetrical': 'False', 'to': "orm['mks.Member']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'committees.committeemeeting': {
            'Meta': {'object_name': 'CommitteeMeeting'},
            'committee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'meetings'", 'to': "orm['committees.Committee']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'date_string': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mks_attended': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'committee_meetings'", 'symmetrical': 'False', 'to': "orm['mks.Member']"}),
            'protocol_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'topics': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'votes_mentioned': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'committee_meetings'", 'blank': 'True', 'to': "orm['laws.Vote']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'laws.bill': {
            'Meta': {'object_name': 'Bill'},
            'approval_vote': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'bill_approved'", 'unique': 'True', 'null': 'True', 'to': "orm['laws.Vote']"}),
            'first_committee_meetings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'bills_first'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['committees.CommitteeMeeting']"}),
            'first_vote': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bills_first'", 'null': 'True', 'to': "orm['laws.Vote']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'law': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bills'", 'null': 'True', 'to': "orm['laws.Law']"}),
            'pre_votes': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'bills_pre_votes'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['laws.Vote']"}),
            'proposers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'bills'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['mks.Member']"}),
            'second_committee_meetings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'bills_second'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['committees.CommitteeMeeting']"}),
            'stage': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'stage_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        },
        'laws.govlegislationcommitteedecision': {
            'Meta': {'object_name': 'GovLegislationCommitteeDecision'},
            'bill': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'gov_decisions'", 'null': 'True', 'to': "orm['laws.Bill']"}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'stand': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'subtitle': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        },
        'laws.govproposal': {
            'Meta': {'object_name': 'GovProposal'},
            'bill': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'gov_proposal'", 'unique': 'True', 'null': 'True', 'to': "orm['laws.Bill']"}),
            'booklet_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'committee_meetings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'laws_govproposal_related'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['committees.CommitteeMeeting']"}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'knesset_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'law': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'laws_govproposal_related'", 'null': 'True', 'to': "orm['laws.Law']"}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'votes': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'laws_govproposal_related'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['laws.Vote']"})
        },
        'laws.knessetproposal': {
            'Meta': {'object_name': 'KnessetProposal'},
            'bill': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'knesset_proposal'", 'unique': 'True', 'null': 'True', 'to': "orm['laws.Bill']"}),
            'booklet_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'committee': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bills'", 'null': 'True', 'to': "orm['committees.Committee']"}),
            'committee_meetings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'laws_knessetproposal_related'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['committees.CommitteeMeeting']"}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'knesset_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'law': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'laws_knessetproposal_related'", 'null': 'True', 'to': "orm['laws.Law']"}),
            'originals': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'knesset_proposals'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['laws.PrivateProposal']"}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'votes': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'laws_knessetproposal_related'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['laws.Vote']"})
        },
        'laws.law': {
            'Meta': {'object_name': 'Law'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'merged_into': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'duplicates'", 'null': 'True', 'to': "orm['laws.Law']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        },
        'laws.membervotingstatistics': {
            'Meta': {'object_name': 'MemberVotingStatistics'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'voting_statistics'", 'unique': 'True', 'to': "orm['mks.Member']"})
        },
        'laws.partyvotingstatistics': {
            'Meta': {'object_name': 'PartyVotingStatistics'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'party': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'voting_statistics'", 'unique': 'True', 'to': "orm['mks.Party']"})
        },
        'laws.privateproposal': {
            'Meta': {'object_name': 'PrivateProposal'},
            'bill': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'proposals'", 'null': 'True', 'to': "orm['laws.Bill']"}),
            'committee_meetings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'laws_privateproposal_related'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['committees.CommitteeMeeting']"}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'joiners': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'bills_joined'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['mks.Member']"}),
            'knesset_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'law': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'laws_privateproposal_related'", 'null': 'True', 'to': "orm['laws.Law']"}),
            'proposal_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'proposers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'bills_proposed'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['mks.Member']"}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'votes': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'laws_privateproposal_related'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['laws.Vote']"})
        },
        'laws.vote': {
            'Meta': {'object_name': 'Vote'},
            'against_party': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'controversy': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'full_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'full_text_url': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'importance': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'meeting_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'src_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'src_url': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'time_string': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'vote_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'votes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'votes'", 'blank': 'True', 'through': "orm['laws.VoteAction']", 'to': "orm['mks.Member']"}),
            'votes_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'laws.voteaction': {
            'Meta': {'object_name': 'VoteAction'},
            'against_coalition': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'against_opposition': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'against_party': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mks.Member']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'vote': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['laws.Vote']"})
        },
        'mks.member': {
            'Meta': {'object_name': 'Member'},
            'area_of_residence': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'blog': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['planet.Blog']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'current_party': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'members'", 'null': 'True', 'to': "orm['mks.Party']"}),
            'current_role_descriptions': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_of_death': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'family_status': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'is_current': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'number_of_children': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parties': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'all_members'", 'symmetrical': 'False', 'through': "orm['mks.Membership']", 'to': "orm['mks.Party']"}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'place_of_birth': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'place_of_residence': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'place_of_residence_lat': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'place_of_residence_lon': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'residence_centrality': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'residence_economy': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'year_of_aliyah': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'mks.membership': {
            'Meta': {'object_name': 'Membership'},
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mks.Member']"}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mks.Party']"}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'mks.party': {
            'Meta': {'object_name': 'Party'},
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_coalition': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'number_of_members': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'number_of_seats': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'planet.blog': {
            'Meta': {'object_name': 'Blog'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '1024', 'db_index': 'True'})
        },
        'tagging.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        },
        'tagging.taggeditem': {
            'Meta': {'unique_together': "(('tag', 'content_type', 'object_id'),)", 'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': "orm['tagging.Tag']"})
        }
    }

    complete_apps = ['laws']
