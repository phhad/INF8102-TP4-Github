import boto3
import botocore.exceptions
 
STACK_NAME = "s3-cloudtrail-logging"
TEMPLATE_FILE = "cloudtrail_s3_logging.yaml"
 
cf = boto3.client('cloudformation')
 
# Charger le template CloudFormation
with open(TEMPLATE_FILE, "r") as f:
    template_body = f.read()
 
def deploy_stack(stack_name, template_body):
    try:
        print(" Déploiement du stack CloudTrail S3...")
        cf.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Capabilities=['CAPABILITY_NAMED_IAM']
        )
        print(f" Stack '{stack_name}' déployé avec succès.")
    except cf.exceptions.AlreadyExistsException:
        try:
            print(" Stack déjà existant, tentative de mise à jour...")
            cf.update_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Capabilities=['CAPABILITY_NAMED_IAM']
            )
            print(f" Stack '{stack_name}' mis à jour avec succès.")
        except botocore.exceptions.ClientError as e:
            if "No updates are to be performed" in str(e):
                print(" Aucun changement à déployer.")
            else:
                print(" Erreur :", e.response['Error']['Message'])
 
deploy_stack(STACK_NAME, template_body)