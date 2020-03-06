# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

SAMWISE_CONFIGURATION_FILE = "~/.samwise"
DEFAULT_TEMPLATE_FILE_PATH = ".samwise"
SAMWISE_TEMPLATE_FILE_NAME = "samwise.yaml"
AWS_SAM_TEMPLATE_FILE_NAME = "template.yaml"
SAMWISE_SUPPORTED_VERSIONS = ["1.0"]


# Metadata
CFN_METADATA_KEY = 'Metadata'
TAGS_KEY = "Tags"
VARS_KEY = "Variables"
SAMWISE_KEY = "SAMWise"
STACK_NAME_KEY = "StackName"
NAMESPACE_KEY = "Namespace"
DEPLOY_BUCKET_KEY = "DeployBucket"
ACCOUNT_ID_KEY = "AccountId"
DEPLOYBUCKET_NAME_KEY = "DeployBucket"
FILE_INCLUDE_REGEX = rf"(.*)#{{{SAMWISE_KEY}::include ([a-zA-Z0-9./]+)}}"
