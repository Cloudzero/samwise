# SAMWise (Beta)
SAMWise is a tool for packaging and deploying AWS Serverless Application Model applications and an alternative to
the [AWS SAM CLI](https://github.com/awslabs/aws-sam-cli). If you :heart: love the 
AWS Serverless Application Model and living a AWS CloudFormation and AWS native tools lifestyle when building Serverless
applications but found the SAM CLI just a little bit wanting, SAMWise was created for you!

# Language Support:
> Currently only Python is supported, sorry ¯\\\_(ツ)\_/¯
- :snake: Python 3.6 and 3.7

## Why SAMWise
SAMWise was born out of the desire to create the same enjoyable developer experience provided by the
[Serverless Framework](https://www.serverless.com) but while using AWS's 
[Serverless Application Model](https://aws.amazon.com/serverless/sam/) and native tooling as much as possible 
such as the AWS CLI and SAM CLI. The end result is to provide an awesome developer experience that doesn't lock you
into a third party tool if you ever want to switch back to pure SAM/CloudFormation.

### So, what was missing from the AWS CLI and SAM CLI?
One of the greatest things about the Serverless Framework CLI (or `sls`) is its ease of use and flexibility. 
With `sls` you could go from and ideal to your first running Serverless application with just a small amount of yaml and 
a few lines of code with a single command line deploy. In addition `sls` provides a clear indication of success or
failure after deploy along with a nice summary. While all the building blocks are there, none of these properties exist
today with the native AWS tooling. 

*Pure awesome:*

    $ sls deploy -s dev --aws-profile my-account

This just isn't possible with the SAM CLI (or `sam`) which requires at least 4 separate commands, each with 
different command line options to remember. When you are trying to rapidly iterate on a project you might find 
yourself running that `sls` command hundreds of times a day, doing this with `sam` becomes very painful, very fast.

*Not so awesome:*

    $ sam build --use-container
        ...
    $ sam package --s3-bucket my-cool-bucket --profile my-acount
        ...
    $ sam deploy --capabilities CAPABILITY_IAM --region us-east-1 --stack-name my-cool-stack --parameter-overrides Namespace=dev
        ...
    $ aws cloudformation describe-stack-events --stack-name my-cool-stack --profile my-account
        ...

There are a few other items that complicate matters like not being able to do simple variable substitution in
a CloudFormation template, MFA support is poorly thought out and there is no way to extend the build system
(e.g. plugins).

## SAMWise to the rescue
When using SAMWise you have two choices, one you can add a SAMWise block to you SAM template.yaml file and rename it
to samwise.yaml or leave your template.yaml alone and link to it in your samwise.yaml

    SAMWise:
      Version: '1.0'
      DeployBucket: <S3 DEPLOY BUCKET>
      StackName: <YOUR STACK NAME>  # StackName is also provided as a #{Variable} or you can use the AWS:StackName pseudo parameter like a normal CFN template
      SamTemplate: template.yaml    # OPTIONAL if you don't want to touch your template.yaml
      Variables:                    # Provides simple #{Variable} token replacement within your template
        - RuntimeVar                # Will prompt or require via CLI the value for RuntimeVar
        - PreparedVar: SomeValue    # Prepared variable 

Then deploy your functions:

    $ samwise deploy --profile <aws profile name> --namespace <namespace>

## Features
- One line deploy with minimal command line arguments
- Simple template variable substitution
- First class support for MFA (with caching!)

### A note on SAMWise's variable substitution feature
This feature/idea isn't fully baked just yet. It's purpose isn't to add a feature that CloudFormation doesn't have
(it does, mappings), but to allow for an easier, more pleasant on the eyes syntax for setting up mappings.
For the moment however it is simple token substitution, in time however this will evolve to translate variables 
into native CloudFormation mappings before generating the templates so it's very easy to return to pure CloudFormation.    

## Roadmap
Here's what's on the SAMWise roadmap (in priority order:
1. Better packaging
    - Right now, SAMWise uses the SAM CLI for packaging, but it's slow, doesn't cache much, and
    packages everything regardless if that code has changed or not. 
    - Your code should be namespaced, right now your functions get thrown into the same folder with your package dependencies and it's only matter of time before a
    collision occurs
2. During/Post-Deployment stats and notifications
    - Currently deployment output sucks and is practically non-existent, this is however one of the main goals of this
    tool so it's coming soon. No rest for the wicked and all that...
3. Support more run-times
    - It would be nice to support more run-times than just Python. This is where the SAM CLI actually has done an
    amazing job and SAMWise has not
    - If SAMWise starts to show promise, then Javascript would likely be next 

### Contributing
SAMWise has only one contributor right now but PR's and bug reports are welcome! If you want to discuss SAMWise, 
Serverless or even the weather, please feel free to reach me (Erik) on Twitter at [@silvexis](https://twitter.com/@silvexis), DM's are open and welcome.

### Last word
SAMWise exists to fill a need that right now the native tools from AWS do not and were preventing me from migrating from
the Serverless framework to SAM. I would love nothing more than to sit down with the AWS SAM CLI team and figure out how
to end-of-life SAMWise. Until then, well, development waits for no one!