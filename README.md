# Testing readiness of Enterprise Linuxes on IPv6-only networking
## How to deploy
### Install Pulumi
[Install](https://www.pulumi.com/docs/clouds/aws/get-started/begin/#install-pulumi) Pulumi.

If you don't have a Pulumi Cloud account, switch Pulumi backend from Pulumi Cloud to local filesystem.

```sh
pulumi login --local
```

The state will be stored on the local filesystem now.

Initialize stack.

```sh
pulumi stack init ipv6_only_testing
```

### Authorization

Use [documentation](https://www.pulumi.com/registry/packages/aws/installation-configuration/#credentials) of AWS Classic Provider for available method for configuring credentials.

If you already setup multiple AWS accounts by profiles.

```sh
pulumi config set aws:profile 'foo'
pulumi config set aws-native:profile 'foo'
```

You also need to set region for AWS Native provider even an aws profile was set.

example aws region: `us-east-1`
```sh
pulumi config set aws-native:region 'us-east-1'
```

### Required Input Variables

Set IPv4 CIDR for the default VPC. Something minimal like `192.168.3.0/24-192.168.255.0/24` is enough.

example IPv4 CIDR: `192.0.2.0/24`
```sh
pulumi config set vpc_cidr_block_ipv4 '192.0.2.0/24'
```

The name of public SSH key that already imported to AWS.

example key name: `foo`
```sh
pulumi config set ssh_key_name 'foo'
```

### Optional Input Variables

EC2 instance type for x86_64 and AArch64 based instances.

example: `t3.small` for x86_64 and `t4g.small` for AArch64.
```sh
pulumi config set ec2_instance_type_x86_64 't3.small'
pulumi config set ec2_instance_type_aarch64 't4g.small'
```

Allowed IPv4 CIDR for SSH inbound connection.

example: Only for `192.0.2.42`
```sh
pulumi config set allowed_cidr_ipv4_ssh '192.0.2.42/32'
```

You can also set the availability zone if desired EC2 instance type is not available on the dynamically chosen one

```sh
pulumi config set az 'us-east-1f'
```

### Deploy

Install Providers and their dependencies and preview changes.

```sh
pulumi preview
```

Deploy.

```sh
pulumi up
```

### Testing

Connect IPv6-only machines through SSH jump host.

```sh
ssh -J ec2-user@$PUBLIC_IPv4_JUMPHOST ec2-user@$IPv6
```

Cloud-init log files:
- `/var/log/cloud-init-output.log`
- `/var/log/cloud-init.log`

These two lines means that IMDS works and used by Cloud-init to fetch meta data.

`/var/log/cloud-init.log`
```sh
url_helper.py[DEBUG]: Read from http://[fd00:ec2::254]/latest/api/token (200, 56b) after 1 attempts
DataSourceEc2.py[DEBUG]: Using metadata source: 'http://[fd00:ec2::254]'
```

Query the IMDS.

```sh
TOKEN=$(curl -X PUT "http://[fd00:ec2::254]/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600") && curl -H "X-aws-ec2-metadata-token: $TOKEN" http://[fd00:ec2::254]/latest/meta-data
```

expected output.

```sh
ami-id
ami-launch-index
ami-manifest-path
block-device-mapping/
events/
hibernation/
hostname
identity-credentials/
instance-action
instance-id
instance-life-cycle
instance-type
ipv6
local-hostname
mac
metrics/
network/
placement/
profile
public-keys/
reservation-id
security-groups
services/
system
```

### Destroy

Destroy.

```sh
pulumi destroy
```
