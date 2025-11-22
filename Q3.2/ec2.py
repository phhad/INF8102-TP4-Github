from troposphere import Template, Ref, Tags, GetAtt
import troposphere.ec2 as ec2
from troposphere.iam import InstanceProfile
from troposphere.cloudwatch import Alarm, MetricDimension
 
template = Template()
template.set_description("TP4 - EC2 avec LabRole et CloudWatch Alarm sur NetworkIn")
 
# Exemple de Subnet, VPC, et SecurityGroup à réutiliser depuis ton code précédent
vpc_id = "vpc-0917f783d140ce914"
public_subnet_id_az1 = "subnet-074bae4ad43499cd2"
public_subnet_id_az2 = "subnet-0cbde4dccaf932110"
private_subnet_id_az1 = "subnet-0a8fc5711de2ce763"
private_subnet_id_az2 = "subnet-004dc9f9165e52ff7"
sg_id = "sg-06b11d49588ee1605"
 
# 1. Associer LabRole via InstanceProfile
instance_profile = template.add_resource(InstanceProfile(
    "LabInstanceProfile",
    Roles=["LabRole"]
))
 
# 2. Créer les instances EC2 publiques et privées
instances = []
for i, subnet in enumerate([public_subnet_id_az1, public_subnet_id_az2]):
    instance = template.add_resource(ec2.Instance(
        f"PublicInstanceAZ{i+1}",
        ImageId="ami-0abac8735a38475db",  # Remplace avec ton AMI ID
        InstanceType="t3.micro",
        SubnetId=subnet,
        SecurityGroupIds=[sg_id],
        IamInstanceProfile=Ref(instance_profile),
        Tags=Tags(Name=f"PublicInstanceAZ{i+1}")
    ))
    instances.append(instance)
 
for i, subnet in enumerate([private_subnet_id_az1, private_subnet_id_az2]):
    instance = template.add_resource(ec2.Instance(
        f"PrivateInstanceAZ{i+1}",
        ImageId="ami-0f8f4e8fb1da4298f",  # Remplace avec ton AMI ID
        InstanceType="t3.micro",
        SubnetId=subnet,
        SecurityGroupIds=[sg_id],
        IamInstanceProfile=Ref(instance_profile),
        Tags=Tags(Name=f"PrivateInstanceAZ{i+1}")
    ))
    instances.append(instance)
 
# 3. CloudWatch Alarms sur NetworkIn
for ec2_instance in instances:
    template.add_resource(Alarm(
        f"{ec2_instance.title}NetworkInAlarm",
        AlarmDescription="Surveille les paquets entrants > 1000",
        Namespace="AWS/EC2",
        MetricName="NetworkIn",
        Dimensions=[
            MetricDimension(
                Name="InstanceId",
                Value=Ref(ec2_instance)
            )
        ],
        Statistic="Average",
        Period=60,
        EvaluationPeriods=1,
        Threshold=1000,
        ComparisonOperator="GreaterThanThreshold",
        AlarmActions=[],  # À compléter si besoin
        Unit="Bytes"
    ))
 
# Génération du template YAML
with open("ec2_with_alarm.yaml", "w") as f:
    f.write(template.to_yaml())
 
print(" Fichier 'ec2_with_alarm.yaml' généré avec succès.")