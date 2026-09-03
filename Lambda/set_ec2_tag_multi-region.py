import boto3

REGIONS = [
    "eu-west-1",
    "us-west-2"
]

def lambda_handler(event, context):
    processed_count = 0

    for region in REGIONS:
        print(f"Processing region: {region}")
        
        ec2 = boto3.client(
            "ec2",
            region_name=region
        )

        paginator = ec2.get_paginator("describe_instances")

        page_iterator = paginator.paginate(
            Filters=[
                {
                    "Name": "instance-state-name",
                    "Values": ["running"]
                }
            ]
        )

        for page in page_iterator:
            for reservation in page["Reservations"]:
                for instance in reservation["Instances"]:

                    instance_id = instance["InstanceId"]
                    architecture = instance.get("Architecture")

                    print(
                        f"Processing instance: "
                        f"{instance_id}, "
                        f"region: {region}, "
                        f"architecture: {architecture}"
                    )

                    if architecture == "arm64":
                        tags = [
                            {
                                "Key": "sec-graviton-migration",
                                "Value": "post-migration"
                            }
                        ]

                    elif architecture == "x86_64":
                        tags = [
                            {
                                "Key": "sec-graviton-migration",
                                "Value": "pre-migration"
                            }
                        ]

                    else:
                        tags = [
                            {
                                "Key": "sec-graviton-migration",
                                "Value": "none-migration"
                            }
                        ]

                    ec2.create_tags(
                        Resources=[instance_id],
                        Tags=tags
                    )

                    processed_count += 1

                    print(
                        f"Tags updated: "
                        f"{region} / {instance_id} -> {tags}"
                    )

    return {
        "statusCode": 200,
        "processedInstances": processed_count
    }
