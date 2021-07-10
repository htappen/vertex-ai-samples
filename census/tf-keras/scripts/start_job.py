import click
import datetime
import google.auth
import os
import re
import subprocess

from google.cloud import aiplatform
from google.cloud import storage


CONTINENT_RE = re.compile('^[^-]+')
LOCAL_FILENAME = 'dist/trainer-0.1.tar.gz'
GS_FILENAME = 'train/trainer-0.1.tar.gz'

def package_app(project, bucket):
  subprocess.run(
    'python setup.py sdist',
    shell=True
  )

  client = storage.Client(project=project)
  bucket = client.get_bucket(bucket)
  blob = bucket.blob(GS_FILENAME)
  blob.upload_from_filename(filename=LOCAL_FILENAME)
  return os.path.join('gs://', bucket.name, GS_FILENAME)

def start_job(project, location, bucket, package):
  client = aiplatform.gapic.JobServiceClient(client_options={
    'api_endpoint': f'{location}-aiplatform.googleapis.com'
  })
  continent = CONTINENT_RE.search(location).group(0)

  parent = f'projects/{project}/locations/{location}'
  custom_job = {
    'display_name': f'penguins_train_{datetime.datetime.now().strftime("%s")}',
    'job_spec': {
      'base_output_directory': {
        'output_uri_prefix': bucket
      },
      'worker_pool_specs': [
        {
          'machine_spec': {
            'machine_type': 'n1-standard-4',
          },
          'replica_count': 1,
          'python_package_spec': {
            'executor_image_uri': f'{continent}-docker.pkg.dev/vertex-ai/training/tf-cpu.2-4:latest',
            'package_uris': [package],
            'python_module': 'trainer.task'
          }
        }
      ]
    }
  }

  response = client.create_custom_job(parent=parent, custom_job=custom_job)
  return response


@click.command()
@click.option('--project')
@click.option('--staging_bucket', required=True)
@click.option('--location', default='us-central1')
def main(
  project,
  staging_bucket,
  location,
):
  if project is None:
    _, project = google.auth.default()
  package_gs_path = package_app(project, staging_bucket)
  print('Package uploaded to:', package_gs_path)
  out_path = os.path.join('gs://', staging_bucket, 'output')
  start_job(project, location, out_path, package_gs_path)
  
if __name__ == '__main__':
    main()