# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import boto3
import botocore.credentials
import botocore.exceptions
import botocore.session


def get_aws_session(aws_profile, region_name=None, aws_credentials=None):
    """
    Create and return a boto3 session object using previously retrieved AWS credentials

    Low probability bugs in this approach that need to be fixed one day
    todo :  Check if credentials have expired before creating session object

    Args:
        aws_profile:
        region_name:
        aws_credentials:

    Returns:

    """
    if not region_name:
        region_name = 'us-east-1'

    if not aws_credentials:
        aws_credentials = get_aws_credentials(aws_profile)

    session = boto3.Session(aws_access_key_id=aws_credentials['AWS_ACCESS_KEY_ID'],
                            aws_secret_access_key=aws_credentials['AWS_SECRET_ACCESS_KEY'],
                            aws_session_token=aws_credentials['AWS_SESSION_TOKEN'],
                            region_name=region_name)

    return session


def get_aws_credentials(profile_name, duration=None):
    """
    Get AWS Credentials for a given profile

    Why do we get credentials like this and not just create a boto3 session or something? Glad you asked!

    In the real world, people use AWS profiles because they have _lots_ of AWS accounts, so first and foremost,
    aws profiles _must_ be handled easily. But that's not the primary concern here.

    In the real real world, people also use MFA. Why? Well for starters AWS TELLS YOU it's a best practice, and you
    know what, it really is. Why however don't a lot of people use MFA? Well it's because the people building tools
    never treat it seriously and do no testing with MFA. Every AWS tools developer should work with MFA
    set to ON for everything they do, trust me, once you do this, the MFA experience will get fixed real fast.

    So, with all that in mind, what this approach to getting AWS credentials enables is:
    1. Get the MFA process out of the way upfront as the _first_ thing the app prompts you for so you don't have to sit
       around waiting for a prompt
    2. Use the built in ability of Boto3 to cache the MFA credentials so you don't have to go find your token
       every time you run the tool
    3. Support shelling out to AWS aware tools (like the SAM CLI)
    4. Also support using the cached credentials when creating Botocore/Boto3 sessions (you have to pass in the keys vs.
       using a profile_name but that's a small price to pay for awesomeness)

    Args:
        profile_name (str): A AWS profile name, as defined in the users .aws/aws_credentials file
        duration (int): Session duration in seconds, the duration configured in the role policy takes precedence

    Returns:
        (dict):
    """
    if not duration:
        duration = 3600

    # Construct low level botocore session with cache, which allows MFA session reuse
    if profile_name:
        session = botocore.session.Session(profile=profile_name)
        mfa_serial = session.full_config['profiles'][profile_name].get('mfa_serial')
    else:
        session = botocore.session.Session()
        mfa_serial = None

    session.get_component('credential_provider').get_provider('assume-role').cache = \
        botocore.credentials.JSONFileCache()

    # this mfa_serial code is _only_ here to deal with boto profiles that _do not_ assume a role
    # which is required because this PR is still open: https://github.com/boto/botocore/pull/1399
    # otherwise MFA is nicely handled automatically by boto. Sadly, these credentials are not cached
    if mfa_serial and not session.full_config['profiles'][profile_name].get('role_arn'):
        sts = session.create_client('sts')
        mfa_code = input("Enter MFA code for {}: ".format(mfa_serial))
        response = sts.get_session_token(DurationSeconds=duration, SerialNumber=mfa_serial, TokenCode=mfa_code)
        credentials = response['Credentials']
        identity = sts.get_caller_identity()
        env_vars = {'AWS_ACCESS_KEY_ID': credentials['AccessKeyId'],
                    'AWS_SECRET_ACCESS_KEY': credentials['SecretAccessKey'],
                    'AWS_SESSION_TOKEN': credentials['SessionToken'],
                    'AWS_ACCOUNT_ID': identity.get('Account')}
        print('.')
    else:
        credentials = session.get_credentials()
        sts = session.create_client('sts')
        identity = sts.get_caller_identity()
        env_vars = {'AWS_ACCESS_KEY_ID': credentials.access_key,
                    'AWS_SECRET_ACCESS_KEY': credentials.secret_key,
                    'AWS_SESSION_TOKEN': credentials.token,
                    'AWS_ACCOUNT_ID': identity.get('Account')}
    return env_vars
