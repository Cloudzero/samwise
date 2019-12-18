# SAMWise (Beta)
> “Come on, Mr. Frodo. I can’t carry it for you… but I can carry you!” -- Samwise Gamgee, Lord of the Rings

If you :heart: love the AWS Serverless Application Model, CloudFormation and living an AWS native lifestyle but
found the SAM CLI just a little bit wanting, SAMWise was created for you

SAMWise was designed to carry the [AWS SAM CLI](https://github.com/awslabs/aws-sam-cli) by wrapping the necessary CLI commands to provide a delightful [Serverless Application Model](https://aws.amazon.com/serverless/sam/) packaging and deployment experience.


## Why SAMWise
SAMWise was born out of the desire to create the same enjoyable developer experience provided by the
[Serverless Framework](https://www.serverless.com) but while using AWS's 
[Serverless Application Model](https://aws.amazon.com/serverless/sam/) and native tooling as much as possible.

SAMWise's primary goal is to provide that same awesome developer experience without locking you into a third party tool,
(even including this one!) If you ever want to switch back to pure SAM/CloudFormation, SAMWise doesn't judge and will
support you there and back again.

### So, what was missing from the AWS CLI and SAM CLI?
One of the greatest things about the Serverless Framework CLI (or `sls`) is its ease of use and flexibility. 
With `sls` you could go from an idea to your first running Serverless application with just a small amount of yaml, 
a few lines of code and a single command line deploy.

While all the building blocks are there with the AWS CLI, SAM CLI and API's, the native AWS tooling (at least today)
falls just short of this goal :disappointed:

#### Example:

The latest version SAM CLI (or `sam`) has made some great improvements, reducing the number of commands you need
to run to only 2, producing nice status output and if you use the `--guided` option and eliminating the need to
remember the command line options with every run. However it's still not without some challenges. Juggling AWS profiles, MFA prompts and namespacing things are still not as easy as they should be. When you are trying to
rapidly iterate on a project you might find yourself deploying hundreds of times a day, doing this with `sam` alone
is still more painful than it should be.

**Close(!) but not quite there yet:**

    $ sam build --use-container
        ...
    $ sam deploy --capabilities CAPABILITY_IAM --region us-east-1 --stack-name my-cool-stack --parameter-overrides Namespace=dev
        ...

There are a few other items that complicate matters like not being able to do simple variables in
a CloudFormation template (I'm sorry, but mappings are just plain ugly), Multi-Factor Auth (MFA) support is poorly thought out
(requires multiple prompts and doesn't cache!) and there is no way to extend or optimize the build system (e.g. plugins).

### SAMWise to the rescue
SAMWise can be used in one of two ways. You can add a SAMWise block to the `Metadata` section of your SAM
`template.yaml` file and rename it to `samwise.yaml` or leave your `template.yaml` 100% alone (and valid CFN)
and link to it in your `samwise.yaml`

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
namespace liberally throughout your template wherever you name things to avoid stack collisions and allow you to
deploy multiple instantiations of your systems.  

## Features
- One line deploy with minimal command line arguments
- Simple namespacing and template variable substitution
- First class support for MFA (with caching!)

### A note on SAMWise's variable substitution feature
This feature/idea isn't fully baked just yet. It's purpose isn't to add a feature that CloudFormation doesn't have
(which it does, mappings), but to allow for a more pleasant, easier on the eyes syntax for setting up mappings.
For the moment it is simple token substitution, in time however this will evolve to translate variables 
into native CloudFormation mappings before generating the final templates so it will be very easy to return to
pure CloudFormation.    

### Language Support:
> Currently only Python is supported, sorry ¯\\\_(ツ)\_/¯
- :snake: Python 3.6 and 3.7

## Installation

    $ pip install samwise
    
## Usage
    
    $ samwise --help
      SAMWise - Tools for better living with the AWS Serverless Application model and CloudFormation

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

## Roadmap
Here's what's on the SAMWise roadmap (in priority order):
1. Smart building and packaging. 
    * Currently we straight up use `sam build -u` which is fine, but it's slow. For starters, if I don't touch the package requirements.txt, don't rebuild all the packages! There is a lot of room for improvement here.
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
