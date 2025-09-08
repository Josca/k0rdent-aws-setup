#!/bin/bash
set -eo pipefail

if [ -z "$1" ]; then
  echo "Error: Missing required argument."
  echo "Usage: $0 <k0rdent-user-name>"
  exit 1
fi

secrets_filename="set_k0rdent_user_secrets.sh"

# Setup AWS account
docker run --rm -it \
  -e AWS_REGION -e AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY -e AWS_SESSION_TOKEN \
  -v $(pwd)/scripts:/scripts \
  ghcr.io/josca/k0rdent-aws-setup:0.0.1 /scripts/setup-k0rdent-user.py $1 /scripts/$secrets_filename
source ./scripts/$secrets_filename

# Create k0rdent Kubernetes AWS credentials resources
user_lower=$(echo $1 | tr '[:upper:]' '[:lower:]')
helm upgrade --install aws-cred-$user_lower oci://ghcr.io/k0rdent/catalog/charts/aws-credential \
    --version 0.0.1 \
    -n kcm-system
kubectl patch secret aws-cred-$user_lower-secret -n kcm-system -p='{"stringData":{"AccessKeyID":"'$AWS_ACCESS_KEY_ID_USER'"}}'
kubectl patch secret aws-cred-$user_lower-secret -n kcm-system -p='{"stringData":{"SecretAccessKey":"'$AWS_SECRET_ACCESS_KEY_USER'"}}'
