from troposphere import Template, Ref, Tags, GetAtt
from troposphere.ec2 import VPC, FlowLog
from troposphere.iam import Role, Policy
 
template = Template()
template.set_description("TP4 - VPC avec Flow Logs (REJECT) envoyés dans polystudens3")
 
# --- 1. Créer la VPC ---
vpc = template.add_resource(VPC(
    "PolyStudentVPC",
    CidrBlock="10.0.0.0/16",
    Tags=Tags(Name="polystudent-vpc")
))
 
# --- 2. IAM Role pour Flow Logs -> S3 ---
iam_role = template.add_resource(Role(
    "FlowLogsRole",
    AssumeRolePolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": ["vpc-flow-logs.amazonaws.com"]},
            "Action": ["sts:AssumeRole"]
        }]
    },
    Policies=[Policy(
        PolicyName="AllowS3FlowLogs",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": ["s3:PutObject"],
                "Resource": "arn:aws:s3:::polystudens3-v2/*"   # ← IMPORTANT : mettre ton bucket réel
            }]
        }
    )]
))
 
# --- 3. Flow Log : TrafficType = REJECT + destination S3 ---
flow_log = template.add_resource(FlowLog(
    "PolyStudentVPCFlowLog",
    # DeliverLogsPermissionArn=GetAtt(iam_role, "Arn"),    # ← FIX ICI !!!
    LogDestinationType="s3",
    LogDestination="arn:aws:s3:::polystudens3-v2",       # ← Le bucket réel
    ResourceId=Ref(vpc),
    ResourceType="VPC",
    TrafficType="REJECT"
))
 
# --- 4. Export YAML ---
with open("vpc_with_flowlog.yaml", "w") as f:
    f.write(template.to_yaml())
 
print("Fichier 'vpc_with_flowlog.yaml' généré avec succès.")