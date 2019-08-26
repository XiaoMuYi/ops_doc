# 关于prometheus-operator相关部署手册

## 1. prometheus-operator简单介绍
`prometheus-operator`目前是由`CoreOS`团队进行维护。目前官方推荐的部署方式是通过`helm`进行部署，但是其中有很多限制（目前不支持`hostpath`存储卷的方式，只能通过`PV/PVC`）。

## 2. 部署 prometheus-operator

### 2.1 创建命名空间
```shell
$ kubectl create namespace prometheus-operator
```

#### 2.2 简单部署prometheus-operator
```  shell
$ git clone https://github.com/helm/charts.git
$ cd ./chart/stable/prometheus-operaotr

# 下载 requirements.yaml 文件中的依赖
$ helm dependency update

# 通过 set 方式定义 promethues 配置
$ helm install ./prometheus-operator --namespace prometheus-operator --name prometheus-operator \
    --set prometheus.ingress.enabled=true \
    --set prometheus.ingress.hosts[0]=prometheus.k8s.yongche.org \
    --set prometheus.ingress.annotations."kubernetes\.io/ingress\.class"=traefik \
    --set alertmanager.ingress.enabled=true \
    --set alertmanager.ingress.hosts[0]=alertmanager.k8s.yongche.org \
    --set alertmanager.ingress.annotations."kubernetes\.io/ingress\.class"=traefik \
    --set grafana.ingress.enabled=true \
    --set grafana.ingress.hosts[0]=grafana.k8s.yongche.org \
    --set grafana.ingress.annotations."kubernetes\.io/ingress\.class"=traefik \
    --tls
```

在实际生产环境中，可配置项更多，因此会直接修改 `value.yaml` 文件中的内容来实现（包括指定`storageclass`、`etcd`、`coredns`监控项等）。如果是 `value.yaml` 则执行如下命令进行部署：
```shell
$ helm install ./prometheus-operator01 --namespace prometheus-operator --name prometheus-operator --tls

```
### 2.3 更新配置

```shell
$ helm upgrade prometheus-operator ./prometheus-operator01 --tls
```
### 2.4 删除promethues-operator

```shell
$ helm delete --purge prometheus-operator --tls
$ kubectl delete crd prometheuses.monitoring.coreos.com
$ kubectl delete crd prometheusrules.monitoring.coreos.com
$ kubectl delete crd servicemonitors.monitoring.coreos.com
$ kubectl delete crd alertmanagers.monitoring.coreos.com
```
#### 3. 配置其他

##### 3.1 监控外部etcd集群

首先创建 secret 用户 prometheus 认证

```shell
$ kubectl -n prometheus-operator create secret generic etcd-certs \
    --from-file=/etc/kubernetes/ssl/ca.pem \
    --from-file=/etc/etcd/ssl/etcd.pem \
    --from-file=/etc/etcd/ssl/etcd-key.pem
```
修改 `value.yaml` 文件

```shell
# 修改 prometheus 字段，将上面创建的 etcd-certs 与 prometheus 关联起来。
secrets:
  - etcd-certs
# 开启监控 etcd
kubeEtcd:
  enabled: true
  ## 外部集群IP地址
  endpoints:
    - 172.17.80.26
    - 172.17.80.27
    - 172.17.80.28
  ## 指定 etcd 集群端口
  service:
    port: 2379
    targetPort: 2379
    selector:
      k8s-app: etcd
  ## 配置相关证书
  serviceMonitor:
    scheme: https
    insecureSkipVerify: true
    serverName: etcd.kube-system.svc.cluster.local
    caFile: /etc/prometheus/secrets/etcd-certs/ca.pem
    certFile: /etc/prometheus/secrets/etcd-certs/etcd.pem
    keyFile: /etc/prometheus/secrets/etcd-certs/etcd-key.pem    

```
### 3.2 监控 coredns

```shell
# 监控coredns
coreDns:
  enabled: true
  service:
    port: 9153
    targetPort: 9153
    selector:
      k8s-app: kube-dns
```
### 3.3 监控kubeScheduler和kubeControllerManager 

这俩监控相关简单，在对应的监控项中指定 `endpoint IP` 即可；

### 3.4 配置邮箱及企业微信告警

在 `alertermanager` 项中的 `config` 内容修改为如下：

```shell
    global:
      resolve_timeout: 5m
      smtp_smarthost: 'smtp.exmail.qq.com:465'
      smtp_from: 'shengyang@58coin.com'
      smtp_auth_username: 'shengyang@58coin.com'
      smtp_auth_password: 'WCIwF%7clL'
      smtp_require_tls: false
      wechat_api_url: 'https://qyapi.weixin.qq.com/cgi-bin/'
    route:
      group_by: ['alertname']
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 12h
      receiver: 'email'
      routes:
      - receiver: 'null'
        match:
          alertname: Watchdog
        routes:
      - receiver: 'email'
        continue: true
        group_by: ['alertname']
      - receiver: 'wechat'
        group_by: ['alertname']
        continue: true
    receivers:
    - name: 'null'
    - name: 'email'
      email_configs:
      - to: 'shengyang@58coin.com'
        send_resolved: true
    - name: 'wechat'
      wechat_configs:
      - api_secret: 'XRujhR1JDh8doOeo3kpwUBjBjnedlz5ro4IESpqRMkg'
        send_resolved: true
        to_user: '@all'
        to_party: '2'
        agent_id: '1000002'
        corp_id: 'ww7e0210eb292c005c'
    templates:
      - /etc/alertmanager/config/*.tmpl
```
配置告警模板
```shell
    wechat.tmpl: |
      {{- define "wechat.default.message" -}}
      {{- if gt (len .Alerts.Firing) 0 -}}
      😤Alerts Firing:
      {{ range .Alerts }}
      💔 触发警报: {{ .Labels.alertname }}
      💔 名称空间: {{ .Labels.namespace }}
      💔 涉及主机: {{ .Labels.instance }}
      💔 JOB名称: {{ .Labels.job }}
      💔 容器名称:  {{ .Labels.container }}
      💔 POD名称:  {{ .Labels.pod }}
      💔 告警级别:  {{ .Labels.severity }}
      💔 告警详情:  {{ .Annotations.message }}
      💔 触发时间:  {{ (.StartsAt.Add 28800e9).Format "2006-01-02 15:04:05" }}
      {{- end }}
      {{- end }}
      {{- if gt (len .Alerts.Resolved) 0 -}}
      😆Alerts Resolved:
      {{ range .Alerts }}
      ♥️ 触发警报: {{ .Labels.alertname }}
      ♥️ 名称空间: {{ .Labels.namespace }}
      ♥️ 容器名称: {{ .Labels.container }}
      ♥️ POD名称: {{ .Labels.pod }}
      ♥️ 告警级别: {{ .Labels.severity }}
      ♥️ 告警详情: {{ .Annotations.message }}
      ♥️ 触发时间: {{ (.StartsAt.Add 28800e9).Format "2006-01-02 15:04:05" }}
      ♥️ 恢复时间: {{ (.EndsAt.Add 28800e9).Format "2006-01-02 15:04:05" }}
      {{- end }}
      {{- end }}

```
## 4. 手动部署grafana
### 4.1 启动MySQL数据库

```shell
$ docker run --restart=always -it -d \
         --name grafana-mysql \
         -p 3306:3306 -e MYSQL_ROOT_PASSWORD=my-secret-pw  \
         -v /data/grafana/mysql/database:/var/lib/mysql mysql:5.7.25 \
         --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
```
提示：用于存储 grafana 用户名、模板等信息；

### 4.2 创建相关表

```shell
$ mysql -uroot -p'my-secret-pw'
$ CREATE DATABASE IF NOT EXISTS grafana default charset utf8 COLLATE utf8_general_ci;
$ use grafana;
$ CREATE TABLE `session` (
    `key`       CHAR(16) NOT NULL,
    `data`      BLOB,
    `expiry`    INT(11) UNSIGNED NOT NULL,
    PRIMARY KEY (`key`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
CREATE USER 'grafana' IDENTIFIED BY 'grafana!@#123';
GRANT SELECT,INSERT,UPDATE,DELETE,CREATE ON grafana.* TO `grafana`@`%` identified by 'grafana!@#123';
```

### 4.3 启动grafana容器

```shell
$ docker run --restart=always -it -d \
         -p 3000:3000 \
         -v /etc/hosts:/etc/hosts \
         -e "GF_SERVER_ROOT_URL=http://192.168.112.215:3000" \
         -e "GF_SECURITY_ADMIN_PASSWORD=admin" \
         -e "GF_DATABASE_TYPE=mysql" \
         -e "GF_DATABASE_HOST=192.168.112.215:3306" \
         -e "GF_DATABASE_NAME=grafana" \
         -e "GF_DATABASE_USER=root" \
         -e "GF_DATABASE_PASSWORD=my-secret-pw" \
         -e "GF_DISABLE_GRAVATAR=true" \
         -e "GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource,grafana-piechart-panel" \
         --name grafana \
         grafana/grafana:6.0.2
```

参考链接：  
https://ervikrant06.github.io/kubernetes/Kuberenetes-prometheus-persistent-storage/  
https://multinode-kubernetes-cluster.readthedocs.io/en/latest/03-k8s-helm_and_packages.html  
https://github.com/coreos/prometheus-operator/issues/992  
https://github.com/coreos/prometheus-operator/issues/1121  
https://github.com/coreos/prometheus-operator/issues/1637  
