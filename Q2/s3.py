from troposphere import Template, Ref, Tags
import troposphere.s3 as s3

# Initialiser le template
template = Template()
template.set_description("TP4 - Bucket S3 sécurisé avec KMS, versioning et accès privé")
 
# Créer le bucket S3
bucket = s3.Bucket(
    "PolyStudentS3",
    BucketName="polystudens3-v2",  # changer si le nom est déjà utilisé
    AccessControl="Private",
    VersioningConfiguration=s3.VersioningConfiguration(
        Status="Enabled"
    ),
    BucketEncryption=s3.BucketEncryption(
        ServerSideEncryptionConfiguration=[
            s3.ServerSideEncryptionRule(
                ServerSideEncryptionByDefault=s3.ServerSideEncryptionByDefault(
                    SSEAlgorithm="aws:kms"
                )
            )
        ]
    ),
    Tags=Tags(
        Name="polystudent-s3",
        Projet="TP4"
    )
)
 
template.add_resource(bucket)
 
# Exporter le fichier CloudFormation
with open("s3_bucket.yaml", "w") as f:
    f.write(template.to_yaml())
 
print(" Fichier 's3_bucket.yaml' généré avec succès.")