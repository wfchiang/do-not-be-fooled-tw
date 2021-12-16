import os 

gcloud_url = 'https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-367.0.0-linux-x86_64.tar.gz'

os.system(f'curl -O {gcloud_url}')

os.system('tar -xvf {}'.format(os.path.basename(gcloud_url)))