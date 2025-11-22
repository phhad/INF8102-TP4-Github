import boto3
from datetime import datetime
 
# Buckets
source_bucket = "polystudents3-618480996782"
test_file_key = f"replication-test-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.txt"
 
# Contenu du fichier test
content = "Test de réplication automatique S3 - CloudFormation"
 
# Créer un fichier temporaire local
with open(test_file_key, "w") as f:
    f.write(content)
 
# Envoyer le fichier dans le bucket source
s3 = boto3.client('s3')
s3.upload_file(test_file_key, source_bucket, test_file_key)
 
print(f" Fichier '{test_file_key}' envoyé dans le bucket source : {source_bucket}")
print(" Attends 1 à 5 minutes pour que la réplication s'exécute vers le bucket de destination.")