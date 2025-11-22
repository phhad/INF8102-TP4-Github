import boto3
import botocore.exceptions
 
template_file = "s3_replicate.yaml"
stack_name = "s3-replication-setup"
 
with open(template_file, 'r') as f:
    template_body = f.read()
 
cf = boto3.client('cloudformation')
 
try:
    # Validation du template
    cf.validate_template(TemplateBody=template_body)
    print(" Le template est valide.")
except botocore.exceptions.ClientError as e:
    print("Erreur de validation :", e.response['Error']['Message'])
    exit(1)
 
try:
    # Création du stack
    print("Création du stack CloudFormation...")
    cf.create_stack(
        StackName=stack_name,
        TemplateBody=template_body,
        Capabilities=['CAPABILITY_NAMED_IAM']
    )
    print(f" Stack '{stack_name}' créé avec succès.")
except cf.exceptions.AlreadyExistsException:
    print("Stack déjà existant, tentative de mise à jour...")
 
    try:
        cf.update_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Capabilities=['CAPABILITY_NAMED_IAM']
        )
        print(f" Stack '{stack_name}' mis à jour avec succès.")
    except botocore.exceptions.ClientError as e:
        if "No updates are to be performed" in str(e):
            print("Aucun changement détecté.")
        else:
            print(" Erreur de mise à jour :", e.response['Error']['Message'])