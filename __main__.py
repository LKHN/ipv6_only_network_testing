import pulumi
import pulumi_std
from pulumi_aws_native import ec2 as ec2_native
from pulumi_aws import ec2 as ec2_classic


# Input variables
config = pulumi.Config()


cidr_block_ipv4 = config.require("vpc_cidr_block_ipv4")
key_name = config.require("ssh_key_name")
instance_type_x86_64 = config.get("ec2_instance_type_x86_64") or "t3.micro"
instance_type_aarch64 = config.get("ec2_instance_type_aarch64") or "t4g.micro"
allowed_cidr_ipv4 = config.get("allowed_cidr_ipv4_ssh") or "0.0.0.0/0"
availability_zone = config.get("az")


vpc = ec2_classic.Vpc(
    "ipv6_only_testing",
    assign_generated_ipv6_cidr_block=True,
    cidr_block=cidr_block_ipv4,
)


internet_gateway = ec2_native.InternetGateway(
    "internet_gateway", tags=[{"key": "Name", "value": "IPv6-only Testing IGW"}]
)


vpc_gateway_attachment = ec2_native.VpcGatewayAttachment(
    "ipv6_only_vpc_igw_attachment",
    vpc_id=vpc.id,
    internet_gateway_id=internet_gateway.id,
)


public_route_table_ipv6_only = ec2_native.RouteTable(
    "public_route_table_ipv6_only", vpc_id=vpc.id
)


public_route_table_dualstack = ec2_native.RouteTable(
    "public_route_table_dualstack", vpc_id=vpc.id
)


internet_ipv6_only = ec2_native.Route(
    "route_to_internet_ipv6_only",
    route_table_id=public_route_table_ipv6_only.route_table_id,
    destination_ipv6_cidr_block="::/0",
    gateway_id=internet_gateway.id,
)


internet_ipv4_dualstack = ec2_native.Route(
    "route_to_internet_ipv4",
    route_table_id=public_route_table_dualstack.route_table_id,
    destination_cidr_block="0.0.0.0/0",
    gateway_id=internet_gateway.id,
)


internet_ipv6_dualstack = ec2_native.Route(
    "route_to_internet_ipv6",
    route_table_id=public_route_table_dualstack.route_table_id,
    destination_ipv6_cidr_block="::/0",
    gateway_id=internet_gateway.id,
)


ipv6_cidr_block_1 = vpc.ipv6_cidr_block.apply(
    lambda ipv6_cidr: pulumi_std.cidrsubnet(ipv6_cidr, netnum=0, newbits=8).result
)


ipv6_cidr_block_2 = vpc.ipv6_cidr_block.apply(
    lambda ipv6_cidr: pulumi_std.cidrsubnet(ipv6_cidr, netnum=1, newbits=8).result
)


ipv6_only_subnet = ec2_native.Subnet(
    "ipv6_only_subnet",
    vpc_id=vpc.id,
    assign_ipv6_address_on_creation=True,
    availability_zone=availability_zone,
    ipv6_cidr_block=ipv6_cidr_block_1,
    ipv6_native=True,
)


dualstack_subnet = ec2_native.Subnet(
    "dualstack_subnet",
    vpc_id=vpc.id,
    assign_ipv6_address_on_creation=True,
    availability_zone=availability_zone,
    cidr_block=vpc.cidr_block,
    ipv6_cidr_block=ipv6_cidr_block_2,
)


associate_subnet_route_table_ipv6_only = ec2_native.SubnetRouteTableAssociation(
    "associate_ipv6_only",
    route_table_id=public_route_table_ipv6_only,
    subnet_id=ipv6_only_subnet,
)


associate_subnet_route_table_dualstack = ec2_native.SubnetRouteTableAssociation(
    "associate_dualstack",
    route_table_id=public_route_table_dualstack,
    subnet_id=dualstack_subnet,
)


allow_ssh = ec2_native.SecurityGroupIngress(
    "allow_ssh",
    ip_protocol="tcp",
    cidr_ip=allowed_cidr_ipv4,
    description="Allow inbound SSH access from tcp/22",
    from_port=22,
    to_port=22,
    group_id=vpc.default_security_group_id,
)


# Amazon Machine Images for x86_64
almalinux_9_x86_64 = ec2_classic.get_ami(
    most_recent=True,
    owners=["764336703387"],
    filters=[
        ec2_classic.GetAmiFilterArgs(name="architecture", values=["x86_64"]),
        ec2_classic.GetAmiFilterArgs(name="name", values=["AlmaLinux OS 9.*"]),
    ],
)


rhel_9_x86_64 = ec2_classic.get_ami(
    most_recent=True,
    owners=["309956199498"],
    filters=[
        ec2_classic.GetAmiFilterArgs(name="architecture", values=["x86_64"]),
        ec2_classic.GetAmiFilterArgs(name="name", values=["RHEL-9.4*"]),
    ],
)


centos_stream_9_x86_64 = ec2_classic.get_ami(
    most_recent=True,
    owners=["125523088429"],
    filters=[
        ec2_classic.GetAmiFilterArgs(name="architecture", values=["x86_64"]),
        ec2_classic.GetAmiFilterArgs(name="name", values=["CentOS Stream 9*"]),
    ],
)


# Amazon Machine Images for AArch64
almalinux_9_aarch64 = ec2_classic.get_ami(
    most_recent=True,
    owners=["764336703387"],
    filters=[
        ec2_classic.GetAmiFilterArgs(name="architecture", values=["arm64"]),
        ec2_classic.GetAmiFilterArgs(name="name", values=["AlmaLinux OS 9.*"]),
    ],
)


rhel_9_aarch64 = ec2_classic.get_ami(
    most_recent=True,
    owners=["309956199498"],
    filters=[
        ec2_classic.GetAmiFilterArgs(name="architecture", values=["arm64"]),
        ec2_classic.GetAmiFilterArgs(name="name", values=["RHEL-9.4*"]),
    ],
)


centos_stream_9_aarch64 = ec2_classic.get_ami(
    most_recent=True,
    owners=["125523088429"],
    filters=[
        ec2_classic.GetAmiFilterArgs(name="architecture", values=["arm64"]),
        ec2_classic.GetAmiFilterArgs(name="name", values=["CentOS Stream 9*"]),
    ],
)


ami_ids_x86_64 = {
    "AlmaLinux OS 9 IPv6-only x86_64": almalinux_9_x86_64.image_id,
    "RHEL 9 IPv6-only x86_64": rhel_9_x86_64.image_id,
    "CentOS Stream 9 IPv6-only x86_64": centos_stream_9_x86_64.image_id,
}


ami_ids_aarch64 = {
    "AlmaLinux OS 9 IPv6-only AArch64": almalinux_9_aarch64.image_id,
    "RHEL 9 IPv6-only AArch64": rhel_9_aarch64.image_id,
    "CentOS Stream 9 IPv6-only AArch64": centos_stream_9_aarch64.image_id,
}


for ami_name, ami_id in ami_ids_x86_64.items():
    create_instance = ec2_classic.Instance(
        ami_name,
        ami=ami_id,
        instance_type=instance_type_x86_64,
        key_name=key_name,
        metadata_options=ec2_classic.InstanceMetadataOptionsArgs(
            http_protocol_ipv6="enabled", http_tokens="required"
        ),
        subnet_id=ipv6_only_subnet.id,
        tags={"Name": ami_name},
    )


for ami_name, ami_id in ami_ids_aarch64.items():
    create_instance = ec2_classic.Instance(
        ami_name,
        ami=ami_id,
        instance_type=instance_type_aarch64,
        key_name=key_name,
        metadata_options=ec2_classic.InstanceMetadataOptionsArgs(
            http_protocol_ipv6="enabled", http_tokens="required"
        ),
        subnet_id=ipv6_only_subnet.id,
        tags={"Name": ami_name},
    )


dualstack_ssh_jumphost = ec2_classic.Instance(
    "ssh_jumphost",
    ami=almalinux_9_x86_64.image_id,
    associate_public_ip_address=True,
    instance_type="t3.micro",
    key_name=key_name,
    metadata_options=ec2_classic.InstanceMetadataOptionsArgs(http_tokens="required"),
    subnet_id=dualstack_subnet.id,
    tags={"Name": "DualStack SSH Jumphost"},
)
