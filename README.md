# k0rdent AWS Setup
The repo stores a toolset to automate
[k0rdent AWS onboarding process](https://docs.k0rdent.io/latest/quickstarts/quickstart-2-aws/)

## Usage
Set your AWS admin account credentials:
~~~bash
export AWS_REGION="..." # Any prefered AWS region to create k0rdent related IAM permissions, e.g. us-west-1
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."
~~~

Run main setup script:
~~~bash
git clone git@github.com:Josca/k0rdent-aws-setup.git
cd k0rdent-aws-setup
./setup.sh k0rdentUser
~~~

- This creates AWS IAM user named `k0rdentUser` and assign needed permissions to it. You can create more
users if you need.
- It also creates the permissions in the account if they were not created before.
- Then it creates AWS credentials for the IAM user and Kubernetes Credential object.

## Example
~~~bash
./setup.sh k0rdentTest
~~~
