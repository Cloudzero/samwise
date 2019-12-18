# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

"""SAMWise - Tools for better living with the AWS Serverless Application model and CloudFormation

Usage:
    samwise package --profile <PROFILE> --namespace <NAMESPACE> [--vars <INPUT> --parameter-overrides <INPUT> --s3-bucket <BUCKET> --in <FILE> --out <FOLDER>]
    samwise deploy --profile <PROFILE>  --namespace <NAMESPACE> [--vars <INPUT> --parameter-overrides <INPUT> --s3-bucket <BUCKET> --region <REGION> --in <FILE> --out <FOLDER>]
    samwise generate --namespace <NAMESPACE> [--in <FILE>] [--out <FOLDER> | --print]
    samwise (-h | --help)

Options:
    generate                        Process a samwise.yaml template and produce standard CloudFormation.
    --in <FILE>                     Input file.
    --out <FOLDER>                  Output folder.
    --profile <PROFILE>             AWS Profile to use.
    --namespace <NAMESPACE>         System namespace to distinguish this deployment from others
    --vars <INPUT>                  SAMwise pre-processed variable substitutions (name=value)
    --parameter-overrides <INPUT>   AWS CloudFormation parameter-overrides (name=value)
    --s3-bucket <BUCKET>            Deployment S3 Bucket.
    --region <REGION>               AWS region to deploy to [default: us-east-1].
    --print                         Sent output to screen.
    -y                              Choose yes.
    -? --help                       Usage help.
"""
import os
import sys

from docopt import docopt
from samwise import __version__, constants
from samwise.exceptions import UnsupportedSAMWiseVersion
from samwise.features.template import display, load, save, parse
from samwise.utils.aws import get_aws_credentials
from samwise.utils.cli import execute_and_process


def main():
    arguments = docopt(__doc__)
    aws_profile = arguments.get('--profile')
    deploy_region = arguments.get('--region')
    namespace = arguments.get('--namespace')
    parameter_overrides = arguments.get('--parameter-overrides')

    if aws_profile:
        print(f"SAMWise CLI v{__version__} | AWS Profile: {aws_profile}")
    else:
        print(f"SAMWise CLI v{__version__}")
    print('-' * 100)

    input_file = arguments.get('--in') or constants.DEFAULT_TEMPLATE_FILE_NAME
    input_filepath = os.path.abspath(input_file)
    try:
        template_obj, metadata = load(input_filepath, namespace)
        base_dir = os.path.dirname(input_filepath)
    except FileNotFoundError as error:
        print(f"Could not load input template, {error}")
        sys.exit(1)
    except UnsupportedSAMWiseVersion as error:
        print(error)
        sys.exit(2)

    stack_name = metadata[constants.STACK_NAME_KEY]
    s3_bucket = arguments.get('--s3-bucket') or metadata[constants.DEPLOYBUCKET_NAME_KEY]

    output_location = arguments.get('--out') or constants.DEFAULT_TEMPLATE_FILE_PATH
    if arguments.get('generate'):
        print(f"Generating CloudFormation Template")
        parsed_template_obj = pre_process_template(metadata, output_location, template_obj)
        if arguments.get('--print'):
            print("-" * 100)
            display(parsed_template_obj)

    elif arguments.get('package'):
        aws_creds = get_aws_credentials(aws_profile)
        pre_process_template(metadata, output_location, template_obj)
        sam_package(output_location, base_dir, aws_creds, s3_bucket, parameter_overrides)

    elif arguments.get('deploy'):
        aws_creds = get_aws_credentials(aws_profile)
        pre_process_template(metadata, output_location, template_obj)
        sam_package(output_location, base_dir, aws_creds, s3_bucket, parameter_overrides)
        deploy(aws_creds, aws_profile, deploy_region, output_location, stack_name, namespace, parameter_overrides)
    else:
        print('Nothing to do')


def deploy(aws_creds, aws_profile, deploy_region, output_location, stack_name, namespace, parameter_overrides=None):
    print(f" - Deploying Stack '{namespace}-{stack_name}' to AWS profile '{aws_profile}'")
    # keeping the CFN way around for reference
    # command = ["aws", "cloudformation", "deploy",
    #            "--template-file", f"{output_location}/packaged.yaml",
    #            "--capabilities", "CAPABILITY_IAM", "CAPABILITY_NAMED_IAM",
    #            "--region", deploy_region,
    #            "--stack-name", f"{namespace}-{stack_name}"]
    command = ["sam", "deploy",
               "--template-file", f"{output_location}/packaged.yaml",
               "--capabilities", "CAPABILITY_IAM", "CAPABILITY_NAMED_IAM",
               "--region", deploy_region,
               "--stack-name", f"{namespace}-{stack_name}"]

    if parameter_overrides:
        command.append(["--parameter-overrides", parameter_overrides])
    execute_and_process(command, env=aws_creds)


def sam_package(output_location, base_dir, aws_creds, s3_bucket, parameter_overrides=None):
    print(" - Building package")
    command = ["sam", "build", "--use-container", "-m", "requirements.txt",
               "--build-dir", f"{output_location}/build",
               "--base-dir", base_dir,
               "--template", f"{output_location}/template.yaml"]
    if parameter_overrides:
        command.append(["--parameter-overrides", parameter_overrides])
    execute_and_process(command)

    print(" - Build successful")
    print(f" - Packaging & saving to s3://{s3_bucket}")
    command = ["aws", "cloudformation", "package",
               "--s3-bucket", s3_bucket,
               "--template-file", f"{output_location}/build/template.yaml",
               "--output-template-file", f"{output_location}/packaged.yaml"]
    execute_and_process(command, env=aws_creds)
    print(" - Packaging successful")


def pre_process_template(metadata, output_location, template_obj):
    print(f" - Pre-processing CloudFormation Template")
    parsed_template_obj = parse(template_obj, metadata)
    save(parsed_template_obj, output_location)
    return parsed_template_obj


if __name__ == "__main__":
    main()
