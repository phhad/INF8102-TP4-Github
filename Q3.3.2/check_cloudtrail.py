import boto3
 
client = boto3.client('cloudtrail')
trail_name = "polystudent-trail"
 
try:
    response = client.get_event_selectors(TrailName=trail_name)
    selectors = response.get('EventSelectors', [])
    found_s3 = False
 
    for selector in selectors:
        for data in selector.get('DataResources', []):
            if data['Type'] == 'AWS::S3::Object':
                print(" CloudTrail capture les événements objet S3.")
                for value in data['Values']:
                    print(f"   - Bucket couvert : {value}")
                    found_s3 = True
    if not found_s3:
        print(" Aucun événement objet S3 n’est capturé par ce trail.")
except Exception as e:
    print(f" Erreur lors de la vérification : {str(e)}")