# SAMWise (Beta)
> “Come on, Mr. Frodo. I can’t carry it for you… but I can carry you!” -- Samwise Gamgee, Lord of the Rings

If you :heart: love the AWS Serverless Application Model, CloudFormation and living an AWS native lifestyle but
found the SAM CLI just a little bit wanting, SAMWise was created for you

SAMWise was designed to carry the [Serverless Application Model](https://aws.amazon.com/serverless/sam/) across the
finish line and is a tool for packaging and deploying AWS Serverless Application Model applications.
SAMWise is an alternative to the [AWS SAM CLI](https://github.com/awslabs/aws-sam-cli) (which it uses under the hood).

## Why SAMWise
SAMWise was born out of the desire to create an awesome AWS Serverless developer experience while using AWS's 
[Serverless Application Model](https://aws.amazon.com/serverless/sam/) and native tooling as much as possible.

SAMWise's does not lock you into a third party tool, including itself! If you ever want to switch back to pure 
SAM/CloudFormation, SAMWise doesn't judge and will support you there and back again.

### So, what was missing from the AWS and SAM CLI?
Three things: Simplicity, speed and proper MFA support

One of the greatest things about Serverless is the speed at which you can go from an idea to your first running 
Serverless application with just a small amount of yaml, a few lines of code and a single command line deploy.
Unfortunately while the "hello world" examples promise and even demonstrate this, once you start to build something
significant things start to fall apart. 

Once you start to need to import other 3rd party libraries, you go from one command to run to two and a few commandline
options to remember. If you are using MFA, entering in your MFA code (twice!) per deploy becomes tedious and then there
is the performance of building your packages which is dreadful. Things start to slow down and bloat considerably once
you start to add more than one function.

While all the building blocks are there with the AWS CLI, SAM CLI and API's, the native AWS tooling (at least today) 
falls short of these goal :disappointed:

#### Why not just use the Serverless Framework?
If you are currently a user of the Serverless Framework you have likely noticed that you don't experience any of these
challenges. What if you wanted to live as an AWS native and use native CloudFormation and SAM with a clear
and easy path to backwards compatibility if you ever wanted to revert back to the SAM cli?

### SAMWise to the rescue
SAMWise can be used in one of two ways. You can add a SAMWise block to the `Metadata` section of your SAM
template.yaml file and rename it to samwise.yaml or leave your template.yaml 100% alone (and valid CFN)
and link to it in your samwise.yaml

    Metadata:
      SAMWise:
        Version: '1.0'
        DeployBucket: <S3 DEPLOY BUCKET>
        StackName: <YOUR STACK NAME>  # StackName is also provided as a #{Variable} or you can use the AWS:StackName pseudo parameter like a normal CFN template
        SamTemplate: template.yaml    # OPTIONAL if you don't want to touch your template.yaml
        Variables:                    # Provides simple #{Variable} token replacement within your template
          - RuntimeVar                # Will prompt or require via CLI the value for RuntimeVar
          - PreparedVar: SomeValue    # Prepared variable 

Then deploy your stack:

    $ samwise deploy --profile <aws profile name> --namespace <namespace>
    
Namespace is just a string variable, but it's a required variable and is slightly analogous to `stage`. You should use
namespace liberally throughout your template wherever you name things to avoid collisions and allow you to
deploy multiple instantiations of your stack  

## Features
- One line deploy with minimal command line arguments
- Simple namespaces and template variable substitution
- First class support for MFA (with caching!)
- Super fast and efficient packaging!

### A note on SAMWise's variable substitution feature
This feature/idea is a work in progress. It's purpose isn't to add a feature that CloudFormation doesn't have
(which it does, mappings), but to allow for a more pleasant, easier on the eyes syntax for setting up mappings.
For the moment it is simple token substitution, and that might actually be good enough. In time however this might 
evolve, how, well that depends on you and i'd love to hear your feedback.    

### Language Support:
> Currently only Python is supported, sorry ¯\\\_(ツ)\_/¯
- :snake: Python 3.6 and 3.7

## Installation

    $ pip install samwise
    
## Usage
    
    $ samwise --help
    SAMWise v0.0.4 - Tools for better living with the AWS Serverless Application model and CloudFormation
    
    Usage:
        samwise generate --namespace <NAMESPACE> [--in <FILE>] [--out <FOLDER> | --print]
        samwise package --profile <PROFILE> --namespace <NAMESPACE> [--vars <INPUT> --parameter-overrides <INPUT> --s3-bucket <BUCKET> --in <FILE> --out <FOLDER>]
        samwise deploy --profile <PROFILE>  --namespace <NAMESPACE> [--vars <INPUT> --parameter-overrides <INPUT> --s3-bucket <BUCKET> --region <REGION> --in <FILE> --out <FOLDER>]
        samwise (-h | --help)
    
    Options:
        generate                        Process a samwise.yaml template and produce a CloudFormation template ready for packaging and deployment
        package                         Generate and Package your code (including sending to S3)
        deploy                          Generate, Package and Deploy your code
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

## Roadmap
Here's what's on the SAMWise roadmap (in priority order):
1. Improve variable substitution and support the auto-generation of proper CFN mapping syntax   
1. Support more Languages/runtimes
    - It would be nice to support more than just Python. This is where the SAM CLI actually has done an
    amazing job and SAMWise has not
    - If SAMWise starts to show promise, then Javascript would likely be next 
1. Add plugins

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
