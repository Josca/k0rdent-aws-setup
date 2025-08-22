FROM alpine:3.22

RUN apk add --no-cache python3 py3-pip groff less curl && \
    pip3 install awscli --upgrade --break-system-packages && \
    curl -LO https://github.com/kubernetes-sigs/cluster-api-provider-aws/releases/download/v2.7.1/clusterawsadm-linux-amd64 && \
    install -o root -g root -m 0755 clusterawsadm-linux-amd64 /usr/local/bin/clusterawsadm && \
    rm -rf /var/cache/apk/* /root/.cache /tmp/* clusterawsadm-linux-amd64
