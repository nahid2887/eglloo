# Generated migration for ProjectDocument model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Project_manager', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_name', models.CharField(help_text='Name or title of the document', max_length=300)),
                ('document_type', models.CharField(default='pdf', help_text='File type (pdf, image, doc, etc.)', max_length=50)),
                ('file', models.FileField(help_text='The actual file', upload_to='project_documents/%Y/%m/%d/')),
                ('description', models.TextField(blank=True, help_text='Optional description of the document', null=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='Project_manager.project')),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_project_documents', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-uploaded_at'],
            },
        ),
        migrations.AddIndex(
            model_name='projectdocument',
            index=models.Index(fields=['project', '-uploaded_at'], name='Project_man_project_idx'),
        ),
    ]
