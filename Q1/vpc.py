from troposphere import (
    Template, Ref, Output, Tags, GetAtt, Parameter
)
import troposphere.ec2 as ec2

# Initialiser le template
template = Template()
template.set_description("TP4 - VPC sécurisée avec 2 AZs, sous-réseaux, IGW, NAT, routes et SG - VPC renommée en polystudent-vpc1.")

# Paramètre pour le CIDR du VPC
vpc_cidr_param = template.add_parameter(Parameter(
    "VPCCIDR",
    Type="String",
    Default="10.0.0.0/16",
    Description="CIDR block de la VPC"
))
 
# Créer la VPC renommée : polystudent-vpc1
vpc = template.add_resource(ec2.VPC(
    "PolyStudentVPC",
    CidrBlock=Ref(vpc_cidr_param),
    EnableDnsSupport=True,
    EnableDnsHostnames=True,
    Tags=Tags(Name="polystudent-vpc1")
))
 
# Internet Gateway + Attachment
igw = template.add_resource(ec2.InternetGateway(
    "InternetGateway",
    Tags=Tags(Name="polystudent-igw")
))
 
template.add_resource(ec2.VPCGatewayAttachment(
    "AttachGateway",
    VpcId=Ref(vpc),
    InternetGatewayId=Ref(igw)
))
 
# Sous-réseaux publics et privés dans 2 AZs
public_subnet1 = template.add_resource(ec2.Subnet(
    "PublicSubnetAZ1",
    VpcId=Ref(vpc),
    CidrBlock="10.0.0.0/24",
    AvailabilityZone="ca-central-1a",
    MapPublicIpOnLaunch=True,
    Tags=Tags(Name="Public-AZ1")
))
 
public_subnet2 = template.add_resource(ec2.Subnet(
    "PublicSubnetAZ2",
    VpcId=Ref(vpc),
    CidrBlock="10.0.16.0/24",
    AvailabilityZone="ca-central-1b",
    MapPublicIpOnLaunch=True,
    Tags=Tags(Name="Public-AZ2")
))
 
private_subnet1 = template.add_resource(ec2.Subnet(
    "PrivateSubnetAZ1",
    VpcId=Ref(vpc),
    CidrBlock="10.0.128.0/24",
    AvailabilityZone="ca-central-1a",
    Tags=Tags(Name="Private-AZ1")
))
 
private_subnet2 = template.add_resource(ec2.Subnet(
    "PrivateSubnetAZ2",
    VpcId=Ref(vpc),
    CidrBlock="10.0.144.0/24",
    AvailabilityZone="ca-central-1b",
    Tags=Tags(Name="Private-AZ2")
))
 
# NAT Gateways (nécessite Elastic IPs)
eip1 = template.add_resource(ec2.EIP("EIPAZ1", Domain="vpc"))
eip2 = template.add_resource(ec2.EIP("EIPAZ2", Domain="vpc"))
 
nat1 = template.add_resource(ec2.NatGateway(
    "NatGatewayAZ1",
    AllocationId=GetAtt(eip1, "AllocationId"),
    SubnetId=Ref(public_subnet1),
    Tags=Tags(Name="NAT-AZ1")
))
 
nat2 = template.add_resource(ec2.NatGateway(
    "NatGatewayAZ2",
    AllocationId=GetAtt(eip2, "AllocationId"),
    SubnetId=Ref(public_subnet2),
    Tags=Tags(Name="NAT-AZ2")
))
 
# Route Table publique
pub_rt = template.add_resource(ec2.RouteTable(
    "PublicRouteTable",
    VpcId=Ref(vpc),
    Tags=Tags(Name="Public-RT")
))
 
template.add_resource(ec2.Route(
    "PublicDefaultRoute",
    RouteTableId=Ref(pub_rt),
    DestinationCidrBlock="0.0.0.0/0",
    GatewayId=Ref(igw)
))
 
template.add_resource(ec2.SubnetRouteTableAssociation(
    "PubAZ1Assoc",
    SubnetId=Ref(public_subnet1),
    RouteTableId=Ref(pub_rt)
))
 
template.add_resource(ec2.SubnetRouteTableAssociation(
    "PubAZ2Assoc",
    SubnetId=Ref(public_subnet2),
    RouteTableId=Ref(pub_rt)
))
 
# Route Tables privées
priv_rt1 = template.add_resource(ec2.RouteTable(
    "PrivateRouteTableAZ1",
    VpcId=Ref(vpc),
    Tags=Tags(Name="Private-RT-AZ1")
))
 
priv_rt2 = template.add_resource(ec2.RouteTable(
    "PrivateRouteTableAZ2",
    VpcId=Ref(vpc),
    Tags=Tags(Name="Private-RT-AZ2")
))
 
template.add_resource(ec2.Route(
    "PrivateRouteAZ1",
    RouteTableId=Ref(priv_rt1),
    DestinationCidrBlock="0.0.0.0/0",
    NatGatewayId=Ref(nat1)
))
 
template.add_resource(ec2.Route(
    "PrivateRouteAZ2",
    RouteTableId=Ref(priv_rt2),
    DestinationCidrBlock="0.0.0.0/0",
    NatGatewayId=Ref(nat2)
))
 
template.add_resource(ec2.SubnetRouteTableAssociation(
    "PrivAZ1Assoc",
    SubnetId=Ref(private_subnet1),
    RouteTableId=Ref(priv_rt1)
))
 
template.add_resource(ec2.SubnetRouteTableAssociation(
    "PrivAZ2Assoc",
    SubnetId=Ref(private_subnet2),
    RouteTableId=Ref(priv_rt2)
))
 
# Groupe de sécurité : ports autorisés
sg = template.add_resource(ec2.SecurityGroup(
    "PolyStudentSG",
    GroupDescription="Autorise les ports necessaires",
    VpcId=Ref(vpc),
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(IpProtocol="tcp", FromPort=p, ToPort=p, CidrIp="0.0.0.0/0") for p in [22, 80, 443, 1433, 5432, 3306, 3389, 1514]
    ] + [
        ec2.SecurityGroupRule(IpProtocol="tcp", FromPort=9200, ToPort=9300, CidrIp="0.0.0.0/0"),
        ec2.SecurityGroupRule(IpProtocol="tcp", FromPort=53, ToPort=53, CidrIp="0.0.0.0/0"),
        ec2.SecurityGroupRule(IpProtocol="udp", FromPort=53, ToPort=53, CidrIp="0.0.0.0/0")
    ],
    Tags=Tags(Name="polystudent-sg")
))
 
# Outputs
template.add_output([
    Output("VPC", Value=Ref(vpc)),
    Output("PublicSubnetAZ1", Value=Ref(public_subnet1)),
    Output("PrivateSubnetAZ1", Value=Ref(private_subnet1))
])
 
# Génération du fichier YAML avec le nom demandé
with open("vpc.yaml", "w") as f:
    f.write(template.to_yaml())
 
print("Fichier CloudFormation 'vpc.yaml' généré avec succès.")