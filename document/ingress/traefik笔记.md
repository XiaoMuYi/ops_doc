# 关于kubernetes ingress使用

## 1. traefik 使用

## 1.1 traefik 代理 websocket 应用

我们从[socket.io](https://socket.io/docs/using-multiple-nodes/)官方文档中可以看到对于多节点的介绍，其中通`Nginx`的`ip_hash`配置用得比较多，同一个`ip`访问的请求通过`hash`计算过后会被路由到相同的后端程序。这里我们需要借助 kubernetes services 中提供的参数 `sessionAffinity（也称会话亲和力）`。什么是 `sessionAffinity`？`sessionAffinity`是一个功能，将来自同一个客户端的请求总是被路由回服务器集群中的同一台服务器的能力。

默认情况下`sessionAffinity=None`，会随机选择一个后端进行路由转发的，设置成`ClientIP`后就和上面的`ip_hash`功能一样了。在`kubernetes`中启用`sessionAffinity `很简单，只需要简单的`Service`中配置即可。由于使用的是`traefik ingress`，这里还需要在`Service`中添加一个`traefik`的`annotation`。具体如下参考：

```shell
$ cat dev-tbex-risk-back-core.yaml
---
apiVersion: v1
kind: Service
metadata:
  ...
  annotations:
    traefik.backend.loadbalancer.stickiness: "true"
    traefik.backend.loadbalancer.stickiness.cookieName: "socket"
spec:
  sessionAffinity: "ClientIP"
```

### 1.2 通过 prometheus 监控 traefik

添加如下配置：

```shell
        - --metrics
        - --metrics.prometheus
```

执行如下命令：

```shell
cd ../file/traefik/
kubectl create -f service.yaml
kubectl create -f endpoints.yaml
kubectl create -f servicemonitor.yaml
```
