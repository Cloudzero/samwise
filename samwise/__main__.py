# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

"""SAMWise v${VERSION} - Tools for better living with the AWS Serverless Application model and CloudFormation

Usage:
    samwise generate --namespace <NAMESPACE> [--profile <PROFILE>] [--in <FILE>] [--out <FOLDER> | --print]
    samwise package --namespace <NAMESPACE> [--profile <PROFILE> --vars <INPUT> --parameter-overrides <INPUT> --s3-bucket <BUCKET> --in <FILE> --out <FOLDER>]
    samwise deploy --namespace <NAMESPACE> [--profile <PROFILE> --vars <INPUT> --parameter-overrides <INPUT> --s3-bucket <BUCKET> --region <REGION> --in <FILE> --out <FOLDER>]
    samwise (-h | --help)

Options:
    generate                        Process a samwise.yaml template and produce a CloudFormation template ready for packaging and deployment
    package                         Generate and Package your code (including sending to S3)
    deploy                          Generate, Package and Deploy your code
    --in <FILE>                     Input file.
    --out <FOLDER>                  Output folder.
    --profile <PROFILE>             AWS Profile to use.
    --namespace <NAMESPACE>         System namespace to distinguish this deployment from others
    --vars <INPUT>                  SAMWise pre-processed variable substitutions (name=value)
    --parameter-overrides <INPUT>   AWS CloudFormation parameter-overrides (name=value)
    --s3-bucket <BUCKET>            Deployment S3 Bucket.
    --region <REGION>               AWS region to deploy to [default: us-east-1].
    --print                         Sent output to screen.
    -? --help                       Usage help.
"""
import json
import os
import string
import sys
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from colorama import Fore
from docopt import docopt

from samwise import __version__, constants
from samwise.constants import VARS_KEY
from samwise.exceptions import UnsupportedSAMWiseVersion, InlineIncludeNotFound
from samwise.features.package import build
from samwise.features.template import load, save
from samwise.utils.aws import get_aws_credentials
from samwise.utils.cli import execute_and_process
from samwise.utils.filesystem import hash_directory
from samwise.utils.tools import hash_string, yaml_print, yaml_dumps
from samwise.utils.zip import zipdir


def main():
    doc_string = string.Template(__doc__)
    doc_with_version = doc_string.safe_substitute(VERSION=__version__)
    arguments = docopt(doc_with_version)

    aws_profile = arguments.get('--profile')
    deploy_region = arguments.get('--region')
    namespace = arguments.get('--namespace')
    parameter_overrides = arguments.get('--parameter-overrides') or ""
    parameter_overrides += f" {constants.NAMESPACE_KEY}={namespace}"

    if aws_profile:
        print(f"SAMWise CLI v{__version__} | AWS Profile: {aws_profile}")
    else:
        print(f"SAMWise CLI v{__version__}| AWS Profile via environment")
    print('-' * 100)

    input_file = arguments.get('--in') or constants.DEFAULT_TEMPLATE_FILE_NAME
    output_location = arguments.get('--out') or constants.DEFAULT_TEMPLATE_FILE_PATH
    input_filepath = os.path.abspath(input_file)

    aws_creds = get_aws_credentials(aws_profile)
    aws_account_id = aws_creds['AWS_ACCOUNT_ID']

    print(f"{Fore.LIGHTCYAN_EX} - Loading SAMWise template{Fore.RESET}")
    try:
        template_obj, metadata = load(input_filepath, namespace, aws_account_id)
        base_dir = os.path.dirname(input_filepath)
    except FileNotFoundError as error:
        print(f"{Fore.RED}   - Could not load input template, {error}{Fore.RESET}")
        sys.exit(1)
    except (InlineIncludeNotFound, UnsupportedSAMWiseVersion) as error:
        print(f"{Fore.RED}   - ERROR: {error}{Fore.RESET}")
        sys.exit(2)

    stack_name = metadata['StackName']
    print(f"   - Found stack {stack_name} and processed {len(metadata[VARS_KEY])} SAMWise variables")
    print(f"   - CloudFormation Template rendered to {os.path.abspath(output_location)}/template.yaml")
    save(template_obj, output_location)

    s3_bucket = arguments.get('--s3-bucket') or metadata[constants.DEPLOYBUCKET_NAME_KEY]
    tags = metadata[constants.TAGS_KEY]

    if arguments.get('generate'):
        print(f"Generating CloudFormation Template")
        if arguments.get('--print'):
            print("-" * 100)
            yaml_print(template_obj)
    elif arguments.get('package') or arguments.get('deploy'):
        package(stack_name, template_obj, output_location, base_dir, aws_creds, s3_bucket, parameter_overrides)
        if arguments.get('deploy'):
            deploy(aws_creds, aws_profile, deploy_region, output_location, stack_name, tags, parameter_overrides)
    else:
        print('Nothing to do')


def deploy(aws_creds, aws_profile, deploy_region, output_location, stack_name, tags, parameter_overrides=None):
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
    execute_and_process(command, env=aws_creds)


def package(stack_name, parsed_template_obj, output_location, base_dir, aws_creds, s3_bucket, parameter_overrides=None):
    print(f"{Fore.LIGHTCYAN_EX} - Building Package{Fore.RESET}")

    changes_detected = check_for_code_changes(base_dir, parsed_template_obj['Globals'])
    if changes_detected:
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
        build(parsed_template_obj, output_location, base_dir)
        print(f"{Fore.GREEN}   - Build successful!{Fore.RESET}")
    else:
        print(f"{Fore.GREEN}   - No changes detected, skipping build{Fore.RESET}")

    print(f"   - Saving to s3://{s3_bucket}/{stack_name}", end='')
    try:
        os.remove(f"{output_location}/samwise-pkg.zip")
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


def check_for_code_changes(base_dir, template_globals):
    """

    Args:
        base_dir:
        template_globals:

    Returns:
        Bool: true/false if code has changes
    """
    code_path = template_globals['Function']['CodeUri']
    config_file = Path(constants.SAMWISE_CONFIGURATION_FILE).expanduser()
    if config_file.exists():
        config = json.load(config_file.open())
    else:
        config = {}
    requirements_file = os.path.join(base_dir, "requirements.txt")
    req_modified_time = os.path.getmtime(requirements_file)

    abs_code_path = os.path.abspath(os.path.join(base_dir, code_path))
    src_hash = hash_directory(abs_code_path)

    globals_hash = hash_string(yaml_dumps(template_globals))

    changes = bool(req_modified_time > config.get(requirements_file, 0) or
                   (src_hash != config.get(abs_code_path)) or
                   globals_hash != config.get(f"{code_path}|globals_hash"))

    config[requirements_file] = req_modified_time
    config[abs_code_path] = src_hash
    config[f"{code_path}|globals_hash"] = globals_hash
    json.dump(config, config_file.open('w'))
    return changes


if __name__ == "__main__":
    main()
