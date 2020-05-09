# SAMWise (Beta)
> “Come on, Mr. Frodo. I can’t carry it for you… but I can carry you!” -- Samwise Gamgee, Lord of the Rings

![Build Status](https://cloudzero.semaphoreci.com/badges/samwise.svg) ![Version](https://img.shields.io/pypi/v/samwise?style=flat-square)

If you :heart: love the AWS Serverless Application Model, CloudFormation and living an AWS native lifestyle but
you found the SAM or CloudFormation packaging and deployment process just a little bit wanting, SAMWise was created
for you.

SAMWise carries the [Serverless Application Model](https://aws.amazon.com/serverless/sam/) across the
finish line by using the best of SAM, CloudFormation and the AWS CLI along with a few tricks of it's own for packaging
and deploying AWS Serverless Application Model applications. SAMWise is meant as a drop in an alternative to the
[AWS SAM CLI](https://github.com/awslabs/aws-sam-cli).

## Why SAMWise
SAMWise was born out of the desire to create an awesome AWS Serverless developer experience while using AWS's
[Serverless Application Model](https://aws.amazon.com/serverless/sam/) and native tooling as much as possible.

SAMWise does not lock you into a third party tool, including itself! If you ever want to switch back to pure
SAM/CloudFormation, SAMWise doesn't judge, and will support you there and back again.

### So, what was missing from the AWS and SAM CLI?
Lots of things! Simplicity, speed, the ability to compose templates from mixed sources and proper MFA support

One of the greatest things about Serverless is the speed at which you can go from an idea in your head to your first
running Serverless application with just a small amount of code and a single command line deploy.
Unfortunately while the "hello world" examples promise and even demonstrate this, once you start to build something
significant things start to fall apart.

Once you need to import other 3rd party libraries, you go from one command to run to two and a few commandline
options to remember. Using StepFunctions? You're now embedding JSON inline with your templates. Have aa dozen functions?
The performance of building and deploying your system is dreadful and takes agonizing long. Last but not least, if you
are using MFA (and you should be!), entering in your MFA code (sometimes twice!) with every deploy becomes tedious.

While all the building blocks are there with the AWS CLI, SAM CLI and API's, the native AWS tooling (at least today)
falls short of these goal :disappointed:

#### Why not just use the Serverless Framework?
If you are currently a user of the Serverless Framework you have likely noticed that you don't experience any of these
challenges but what if you wanted to live as an AWS native with a clear conscious. SAMWise lets you use native
CloudFormation with all the speed of Serverless with none of the guilt and a clear and easy path to backwards
compatibility if you ever wanted to revert back to the SAM cli.

### SAMWise to the rescue
Just add a SAMWise block to the `Metadata` section of your existing AWS SAM
template.yaml file and run samwise or leave your `template.yaml` alone
create a `samwise.yaml` and add a link to your `template.yaml`. When you run samwise it will start by looking first for
a `samwise.yaml`, before then trying and load your `template.yaml` and looking for the SAMWise block. If it doesn't find
either, SAMWise will provide some friendly guidance and then safely exit without making any changes. 

    Metadata:
      SAMWise:
        Version: '1.0'
        StackName: <YOUR STACK NAME>     # REQUIRED StackName is also made available as #{SAMWise::StackName} within your template
        DeployBucket: <S3 DEPLOY BUCKET> # OPTIONAL if you don't specify a deploy bucket then the default `SAMWise-deploy-<AWS ACCOUNTID>` will be used 
        SamTemplate: template.yaml       # OPTIONAL if you don't want to touch your template.yaml
        Tags:                            # OPTIONAL Add stack tags to your deployment
          - Name: Value
        Variables:                       # OPTIONAL Provides simple #{Variable} token replacement within your template
          - MyRuntimeVar                 # Variables with no value will prompt at run time for their value
          - MyPreparedVar: SomeValue     # Some Prepared variable

Then deploy your stack:

    $ samwise deploy --profile <aws profile name> --namespace <namespace>

> `--profile` is optional, if not provided, it will use the AWS session configured via environment variables or set as your default profile.

>`--namespace` is required and is a special variable that is slightly analogous to `stage`. It is made available as `#{SAMWise::Namespace}`
> within your template and should be used liberally so you can deploy multiple instantiations of your stack without collisions  

## Features
- One line deploy with minimal command line arguments
- Simple namespaces and template variable substitution using `#{variable}`
- Link in external files using `#{SAMWise::include ./file.json}`
- Super fast and efficient packaging!
- First class support for MFA (with caching!)

### Language Support:
> Currently only Python is supported, sorry ¯\\\_(ツ)\_/¯
- :snake: Python 3.6, 3.7 and 3.8

## Installation

    $ pip install samwise

## Usage

    SAMWise v0.1.1 - Tools for better living with the AWS Serverless Application model and CloudFormation
    
    Usage:
        samwise
        samwise generate --namespace <NAMESPACE> [--profile <PROFILE>] [--in <FILE>] [--out <FOLDER> | --print]
        samwise package --namespace <NAMESPACE> [--profile <PROFILE> --vars <INPUT> --parameter-overrides <INPUT> --s3-bucket <BUCKET> --in <FILE> --out <FOLDER>]
        samwise deploy --namespace <NAMESPACE> [--profile <PROFILE> --vars <INPUT> --parameter-overrides <INPUT> --s3-bucket <BUCKET> --region <REGION> --in <FILE> --out <FOLDER>]
        samwise (--help | --version)
    
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
        -v --version
        -? --help                       Usage help.

## Using SAMWise Variable substitution and external file includes
SAMWise has three types of tokens you can use to substitute content: variables and includes

### Variables
Using the SAMWise metadata section, you can define any number of variables for use within your template.
Once defined, you can insert them anywhere within your template using `#{variable-name}` syntax. Variables
are evaluated before your CloudFormation template and any mappings or parameter overrides are evaluated

### SAMWise::Variables
There are 3 SAMWise variables that can also be used anywhere in your template (including the SAMWise block)
* `#{SAMWise::Namespace}` - Replaced with the namespace you provide via the command line
* `#{SAMWise::StackName}` - Replaced with the stack name you specify in your template
* `#{SAMWise::AccountId}` - Replaced with the account ID of the AWS profile you deploy to

### SAMWise::Include
Have you been spending time with StepFunctions lately? Getting tired of writing JSON inline with YAML?
Wish you could find a nicer editing experience with version control that didn't require you to copy
and paste? If so, SAMWise file includes were made for you! Place whatever file you want to include in
your template wherever you want and use the file include syntax `#{SAMWise::include ./my-file.json}`. Relative
paths are supported. 

## Road map
Here's what's on the SAMWise road map (in priority order):
1. Making packaging even more efficient and fast. Seriously, it can never be _too_ fast.
1. Support more Languages/runtimes
    - It would be nice to support more than just Python. This is where the SAM CLI actually has done an
    amazing job and SAMWise has not
    - If SAMWise starts to show promise, then Javascript would likely be next
1. Add/consider adding plugins support

### Contributing
PR's and bug reports are welcome! If you want to discuss SAMWise, Serverless or even the weather, please feel free to reach out to any of the following contributors:

Maintainer:
- Erik Peterson [@silvexis](https://twitter.com/silvexis)

Contributors:
- Adam Tankanow [@atankanow](https://twitter.com/atankanow)

### Last word
SAMWise exists to fill a need that right now the native tools from AWS do not and were preventing me from migrating from
the Serverless framework to SAM. I would love nothing more than to sit down with the AWS SAM CLI team and figure out how
to end-of-life SAMWise. Until then, well, development waits for no one!
