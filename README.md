# UPDATE! (12/17/2019)
With the release of the new `sam deploy --guided` I had hoped this project will go away. Alas it's still relevant! It still takes two commands to do a deploy and MFA support is still problematic so SAMWise lives on, for now! 

# SAMWise (Beta)
> “Come on, Mr. Frodo. I can’t carry it for you… but I can carry you!” -- Samwise Gamgee, Lord of the Rings

SAMWise was designed to carry the [Serverless Application Model](https://aws.amazon.com/serverless/sam/) across the
finish line and is a tool for packaging and deploying AWS Serverless Application Model applications.
SAMWise is also an alternative to the [AWS SAM CLI](https://github.com/awslabs/aws-sam-cli).

If you :heart: love the AWS Serverless Application Model, CloudFormation and living an AWS native lifestyle but
found the SAM CLI just a little bit wanting, SAMWise was created for you

## Why SAMWise
SAMWise was born out of the desire to create the same enjoyable developer experience provided by the
[Serverless Framework](https://www.serverless.com) but while using AWS's 
[Serverless Application Model](https://aws.amazon.com/serverless/sam/) and native tooling as much as possible.

SAMWise's primary goal is to provide that same awesome developer experience without locking you into a third party tool,
including this one. If you ever want to switch back to pure SAM/CloudFormation, SAMWise doesn't judge and will
support you there and back again.

### So, what was missing from the AWS CLI and SAM CLI?
One of the greatest things about the Serverless Framework CLI (or `sls`) is its ease of use and flexibility. 
With `sls` you could go from an idea to your first running Serverless application with just a small amount of yaml, 
a few lines of code and a single command line deploy.

While all the building blocks are there with the AWS CLI, SAM CLI and API's, the native AWS tooling (at least today)
falls short of this goal :disappointed:

#### Example:

The latest version SAM CLI (or `sam`) has made some great improvements reducing the number of commands you need
to run to only 2, producing nice status output and if you use the `--guided` option, eliminating the need to
remember the command line options with every run. However it's still not without some challenges. MFA prompts
and namespacing things are still not as easy as it should be. You can add parameter overrides to your SAM toml
file, but they probably shouldn't be in there so you are still adding cli options. When you are trying to
rapidly iterate on a project you might find yourself deploying hundreds of times a day, doing this with `sam`
is still more painful than it should be.

**Close(!) but not quite there yet:**

    $ sam build --use-container
        ...
    $ sam deploy --capabilities CAPABILITY_IAM --region us-east-1 --stack-name my-cool-stack --parameter-overrides Namespace=dev
        ...

There are a few other items that complicate matters like not being able to do simple variables in
a CloudFormation template (I'm sorry, but mappings are just plain ugly), MFA support is poorly thought out
(requires multiple prompts and doesn't cache!) and there is no way to extend the build system (e.g. plugins).

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
