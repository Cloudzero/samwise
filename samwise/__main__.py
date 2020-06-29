# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

"""SAMWise v${VERSION} - Tools for better living with the AWS Serverless Application model and CloudFormation

Usage:
    samwise lint --namespace <NAMESPACE> [--profile <PROFILE> --in <FILE> --out <FOLDER>]
    samwise generate --namespace <NAMESPACE> [--profile <PROFILE> --in <FILE>] [--out <FOLDER> | --print]
    samwise package --namespace <NAMESPACE> [--profile <PROFILE> --vars <INPUT> --parameter-overrides <INPUT> --s3-bucket <BUCKET> --in <FILE> --out <FOLDER> --yes --cache-dir <FOLDER>]
    samwise deploy --namespace <NAMESPACE> [--profile <PROFILE> --vars <INPUT> --parameter-overrides <INPUT> --s3-bucket <BUCKET> --region <REGION> --in <FILE> --out <FOLDER> --yes --cache-dir <FOLDER>]
    samwise (--help | --version)

Options:
    lint                            Run cfn-lint against the generated template
    generate                        Process a samwise.yaml template and produce a CloudFormation template ready for packaging and deployment
    package                         Generate and Package your code (including sending to S3)
    deploy                          Generate, Package and Deploy your code
    --in <FILE>                     Input file.
    --out <FOLDER>                  Output folder.
    --cache-dir <FOLDER>            Use specific folder for package caching, otherwise use system default
    --profile <PROFILE>             AWS Profile to use.
    --namespace <NAMESPACE>         System namespace to distinguish this deployment from others
    --vars <INPUT>                  SAMWise pre-processed variable substitutions (name=value)
    --parameter-overrides <INPUT>   AWS CloudFormation parameter-overrides (name=value)
    --s3-bucket <BUCKET>            Deployment S3 Bucket.
    --region <REGION>               AWS region to deploy to [default: us-east-1].
    --print                         Sent output to screen.
    -y --yes                        Answer Yes to any prompts
    -v --version                    Print the SAMWise version number
    -? --help                       Usage help.
"""
import os
import string
import sys
import textwrap
from zipfile import ZipFile, ZIP_DEFLATED

import boto3
import cfnlint.core
from botocore.exceptions import ClientError
from colorama import Fore
from docopt import docopt
from samwise import __version__, constants
from samwise.exceptions import UnsupportedSAMWiseVersion, InlineIncludeNotFound, InvalidSAMWiseTemplate, \
    TemplateNotFound
from samwise.features.package import build, slim_package_folder
from samwise.features.template import load, save
from samwise.utils.aws import get_aws_credentials
from samwise.utils.cli import execute_and_process
from samwise.utils.filesystem import check_for_code_changes
from samwise.utils.tools import yaml_print
from samwise.utils.zip import zipdir


def main():
    doc_string = string.Template(__doc__)
    doc_with_version = doc_string.safe_substitute(VERSION=__version__)
    arguments = docopt(doc_with_version)

    if arguments.get('--version'):
        print(f"SAMWise v{__version__}")
        sys.exit()

    aws_profile = arguments.get('--profile')
    deploy_region = arguments.get('--region')
    namespace = arguments.get('--namespace')
    parameter_overrides = arguments.get('--parameter-overrides') or ""
    parameter_overrides += f" {constants.NAMESPACE_KEY}={namespace}"

    if aws_profile:
        print(f"SAMWise v{__version__} | AWS Profile: {aws_profile}")
    else:
        print(f"SAMWise v{__version__}| AWS Profile via environment")
    print('-' * 100)

    input_file = arguments.get('--in')
    output_path = arguments.get('--out') or constants.DEFAULT_TEMPLATE_FILE_PATH

    aws_creds = get_aws_credentials(aws_profile)
    aws_account_id = str(aws_creds['AWS_ACCOUNT_ID'])

    print(f"{Fore.LIGHTCYAN_EX} - Looking for a SAMWise template{Fore.RESET}")
    try:
        template_path, template_obj, metadata = load(input_file, namespace, aws_account_id)
    except (TemplateNotFound, InlineIncludeNotFound, UnsupportedSAMWiseVersion, InvalidSAMWiseTemplate) as error:
        print(f"{Fore.RED} - ERROR: {error}{Fore.RESET}")
        sys.exit(2)

    stack_name = metadata['StackName']
    print(f"   - Stack {stack_name} loaded")

    save(template_obj, output_path)
    output_file_path = f"{os.path.abspath(output_path)}/template.yaml"
    print(f"   - CloudFormation Template rendered to {output_file_path}")

    if arguments.get('lint'):
        print(f"{Fore.LIGHTCYAN_EX} - Running cfn-lint against generated template{Fore.RESET}")
        results = lint_template(output_file_path)
        if results:
            print(textwrap.indent(results, "   - "))
            sys.exit(1)
    elif arguments.get('generate'):
        if arguments.get('--print'):
            print("-" * 100)
            yaml_print(template_obj)
    elif arguments.get('package') or arguments.get('deploy'):
        base_dir = os.path.dirname(template_path)
        s3_bucket = arguments.get('--s3-bucket') or metadata[constants.DEPLOYBUCKET_NAME_KEY]
        force = bool(arguments.get('package'))  # if packaging was specifically requested, always build
        package(stack_name, template_obj, output_path, base_dir, aws_creds, s3_bucket, parameter_overrides, force,
                arguments.get('--cache-dir'))
        if arguments.get('deploy'):
            upload(aws_creds, output_path, s3_bucket, stack_name)
            tags = metadata[constants.TAGS_KEY]
            deploy(aws_creds, aws_profile, deploy_region, output_path, stack_name, tags, parameter_overrides,
                   confirm=bool(not arguments.get('--yes')))
    else:
        print('Invalid Option')


def lint_template(output_file_path):
    (args, filenames, formatter) = cfnlint.core.get_args_filenames([output_file_path])
    (template, rules, template_matches) = cfnlint.core.get_template_rules(filenames[0], args)
    matches = []
    if not template_matches:
        matches.extend(
            cfnlint.core.run_cli(
                filenames[0], template, rules,
                args.regions, args.override_spec))
    else:
        matches.extend(template_matches)
    return formatter.print_matches(matches)


def package(stack_name, parsed_template_obj, output_location, base_dir, aws_creds, s3_bucket,
            parameter_overrides=None,
            force=False,
            cache_dir=None):
    print(f"{Fore.LIGHTCYAN_EX} - Building Package{Fore.RESET}")

    changes_detected = check_for_code_changes(base_dir, parsed_template_obj['Globals'])
    if changes_detected or force:
        print(f"{Fore.YELLOW}   - Changed detected, rebuilding package{Fore.RESET}")
        # Keeping this here for reference.
        # The sam build way works but is _very_ inefficient and creates packages with
        # potential namespace collisions :-(

        # command = ["sam", "build", "--use-container", "-m", "requirements.txt",
        #            "--build-dir", f"{output_location}/build",
        #            "--base-dir", base_dir,
        #            "--template", f"{output_location}/template.yaml"]
        # if parameter_overrides:
        #     command += ["--parameter-overrides", parameter_overrides.strip()]
        # execute_and_process(command)
        build(parsed_template_obj, output_location, base_dir, cache_dir)
        print(f"{Fore.GREEN}   - Build successful!{Fore.RESET}")
    else:
        print(f"{Fore.GREEN}   - No changes detected, skipping build{Fore.RESET}")

    slim_package_folder(output_location)


def upload(aws_creds, output_location, s3_bucket, stack_name):
    # Create the S3 bucket
    try:
        client = boto3.client(
            's3',
            aws_access_key_id=aws_creds['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=aws_creds['AWS_SECRET_ACCESS_KEY'],
            aws_session_token=aws_creds['AWS_SESSION_TOKEN'],
        )
        client.create_bucket(Bucket=s3_bucket)
    except ClientError as error:
        print(f"FATAL ERROR: Unable to create or verify deployment bucket {error}")
        sys.exit(1)

    print(f"{Fore.LIGHTCYAN_EX} - Saving package to s3://{s3_bucket}/{stack_name}", end='', flush=True)
    try:
        os.remove(f"{output_location}/samwise-pkg.zip")
        os.remove(f"{output_location}/packaged.yaml")
    except OSError:
        pass

    with ZipFile(f"{output_location}/samwise-pkg.zip", 'w',
                 compression=ZIP_DEFLATED,
                 compresslevel=9) as myzip:
        zipdir(f"{output_location}/pkg", myzip)

    command = ["aws", "cloudformation", "package",
               "--s3-bucket", s3_bucket,
               "--s3-prefix", stack_name,
               "--template-file", f"{output_location}/template.yaml",
               "--output-template-file", f"{output_location}/packaged.yaml"]
    execute_and_process(command, env=aws_creds, status_only=True)
    print(f"{Fore.GREEN}   - Upload successful{Fore.RESET}")


def deploy(aws_creds, aws_profile, deploy_region, output_location, stack_name, tags, parameter_overrides=None,
           confirm=False):
    print(f"{Fore.LIGHTCYAN_EX} - Deploying Stack '{stack_name}' using AWS profile '{aws_profile}'{Fore.RESET}")
    # keeping the CFN way around for reference.
    # The new sam deploy way is great!

    # command = ["aws", "cloudformation", "deploy",
    #            "--template-file", f"{output_location}/packaged.yaml",
    #            "--capabilities", "CAPABILITY_IAM", "CAPABILITY_NAMED_IAM",
    #            "--region", deploy_region,
    #            "--stack-name", f"{stack_name}"]

    formatted_tags = " ".join([f"{k}={v}" for tag in tags for k, v in tag.items()])
    print(f"   - Tags:")
    print(f"       {formatted_tags}")

    command = ["sam", "deploy",
               "--template-file", f"{output_location}/packaged.yaml",
               "--capabilities", "CAPABILITY_IAM", "CAPABILITY_NAMED_IAM",
               "--region", deploy_region,
               "--no-fail-on-empty-changeset",
               "--stack-name", f"{stack_name}",
               "--tags", f"{formatted_tags}"]

    if parameter_overrides:
        command += ["--parameter-overrides", parameter_overrides]

    # Re-enable once we figure out how to pass input to stdin
    # if confirm:
    #     command += ["--confirm-changeset"]
    execute_and_process(command, env=aws_creds)


if __name__ == "__main__":
    main()
