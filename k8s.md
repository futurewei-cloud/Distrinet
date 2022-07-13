### Step 1: deploy onos cluster in k8s
```bash
vim onos.yaml
```
```
#onos.yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    app: onos
  name: onos-deployment
spec:
  ports:
  - port: 6653
    protocol: TCP
    targetPort: 6653
    nodePort: 30026
  selector:
    app: onos
  type: NodePort
status:
  loadBalancer: {}
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: onos
  name: onos-deployment
spec:
  replicas: 10
  selector:
    matchLabels:
      app: onos
  template:
    metadata:
      labels:
        app: onos
    spec:
      containers:
      - name: onos
        image: onosproject/onos
        env:
        - name: ONOS_APPS
          value: "drivers,openflow,fwd,proxyarp,lldpprovider"
        args:
          - start
        ports:
        - containerPort: 6653
          name: openflow
        - containerPort: 6640
          name: ovsdb
        - containerPort: 8181
          name: gui
        - containerPort: 8101
          name: onos-cli
        - containerPort: 9876
          name: cluster
```

```bash
kubectl create -f onos.yaml
```

### Step 2: using k8s' onos service as distrinet controller
```bash
python3 bin/dmn --bastion=172.16.66.92 --workers="172.16.66.92,172.16.66.93,172.16.66.94" --controller=lxcremote,ip=192.168.0.1:30026 --topo=linear,2
```
