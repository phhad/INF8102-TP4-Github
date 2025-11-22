import boto3
import botocore.exceptions
 
bucket_name = "polystudents3-618480996782"
 
s3 = boto3.client('s3')
 
try:
    response = s3.get_bucket_replication(Bucket=bucket_name)
    rules = response['ReplicationConfiguration']['Rules']
 
    print(f" La réplication est activée sur le bucket : {bucket_name}")
    for rule in rules:
        print(f"  - Rule ID       : {rule.get('ID')}")
        print(f"    Status        : {rule.get('Status')}")
        print(f"    Destination   : {rule['Destination']['Bucket']}")
        print(f"    Prefix        : {rule.get('Prefix', '') or rule.get('Filter', {}).get('Prefix', '')}")
except botocore.exceptions.ClientError as e:
    error_code = e.response['Error']['Code']
    if error_code == "ReplicationConfigurationNotFoundError":
        print(f" Aucune configuration de réplication trouvée sur le bucket {bucket_name}")
    else:
        print(f" Erreur lors de la vérification : {e.response['Error']['Message']}")