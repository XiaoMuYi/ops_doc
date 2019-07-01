# jenkins pipeline 在 kubernetes 中应用

## 1. jenkins pipeline

`jenkins 2.0`开始推行`Pipeline as Code`，实现从`CI`到`CD`的转变。`pipeline`实际上是一套`Groovy DSL`，用`Groovy`脚本描述`CI/CD`的流程，`jenkins`可以从代码库中获取脚本，实现了`pipeline as Code`。`pipeline`将原来独立运行的多个任务连接起来，可以实现更加复杂的`CI/CD`流程。

为什么要使用`pipeline`？对于实践微服务的团队，产品有很多服务组成，传统的在`jenkins`中集中进行`job`配置的方式会成为瓶颈，微服务团队会将`CI Job`的配置和服务的发布交给具体负责某个服务的团队，这正需要`pipeline as Code`；除此之外，一次产品的发布会涉及到多个服务的协同发布，用单个`CI Job`实现起来会十分困难，使用`pipeline`可以很好的完成这个需求。

### 1.1 基本概念

`node`：一个`node`就是一个`jenkins`节点，可以是`master`，也可以是`slave`，`slave`是`pipeline`中具体`step`的运行环境。

`step`：是最基本的运行单元，可以是创建一个目录、从代码库中`checkout`代码、执行一个`shell`命令、构建`docker`镜像、将服务发布到`kubernetes`集群中。`step`由`jenkins`和`jenkins`各种插件提供。

`stage`：一个`pipeline`有多个`stage`组成，每个`stage`包含一组`step`。注意一个`stage`可以跨多个`node`执行，即`stage`实际上是`step`的逻辑分组。

将`node`、`stage`、`step`的`Groovy DSL`写在一个`jenkinsfile`文件中，`jenkinsfile`会被放到代码库的根目录下。

### 1.2 常用step

由于`jenkins`的`pipeline`是基于`Groovy`的`DSL`，所以使用起来十分简单，编写`jenkinsfile`的过程实际上就是使用各种`step`编排完成`CI/CD`的过程。
参考链接：
`https://jenkins.io/doc/pipeline/steps/`
`https://jenkins.io/doc/pipeline/steps/workflow-basic-steps/`

### 1.3 pipeline举例

`Jenkins Pipeline`支持两种语法，一种`Declarative Pipeline`(声明式)，一种`Scripted Pipeline`(脚本式)。 声明式的`Pipeline`限制用户使用严格的预选定义的结构，是一种声明式的编程模型，对比脚本式的`Pipeline`学习起来更加简单；脚本式的`Pipeline`限制比较少，结构和语法的限制由`Groovy`本身决定，是一种命令式的编程模型。

关于`Pipeline`的语法在编写Pipeline的过程中，参考：https://jenkins.io/doc/book/pipeline/syntax/

**切换当前的目录**

```shell
dir('dir1') {
    sh 'pwd' #如果目录不存在则创建;
}
```

**检出指定分支或`tag`的代码**

```shell
git url: 'ssh://git@gitlab.frognew.com/demo/apidemo.git', branch: 'develop'
```

如果需要获取指定`tag`的代码，需要使用`pipeline: SCM Step`的`checkout`：

```shell
checkout scm: [$class: 'GitSCM',
      userRemoteConfigs: [[url: 'ssh://git@gitlab.frognew.com/demo/apidemo.git']],
      branches: [[name: "refs/tags/1.1.0"]]], changelog: false, poll: false
```

**修改当前构建的名称和描述**

```shell
script {
    currentBuild.displayName = "#${BUILD_NUMBER}(apidemo)"
    currentBuild.description = "publish apidemo"
}
```

**使用Jenkins全局工具**

在`Jenkins -> Manage Jenkins -> Global Tool Configuration`中配置了各种工具，如`JDK、Git、Maven、Gradle、NodeJS、Go、Docker`等等。 每种工具都有一个`Name`，这样不同的`Name`可以配置不同的版本。可以在`Jenkins Pipeline`中使用这些工具，例如下面是一个使用`gradle`构建`java`工程的例子：

```shell
node {
   def javaHome = tool 'JDK1.8'
   def gradleHome = tool 'gradle'
   env.PATH = "${javaHome}/bin:${env.PATH}"
   env.PATH = "${gradleHome}/bin:${env.PATH}"
   stage('build') {
      sh 'gradle clean --refresh-dependencies build -x test'
   }
}
```

**发送邮件通知**

使用`Email Extension Plugin`的`emailext`实现，需要提前在`jenkins`完成`Email Extension Plugin`的配置。

```shell
node {
   try{
      stage('buid') {
         sh 'pwd1'
      }

   }catch(e) {
       emailext (
       subject: "Build failed in Jenkins: '${env.JOB_NAME} #${env.BUILD_NUMBER}'",
       body: """<p>See "<a href="${env.BUILD_URL}">${env.JOB_NAME} #${env.BUILD_NUMBER}</a>"</p>""",
       recipientProviders: [[$class: 'DevelopersRecipientProvider'], [$class: 'RequesterRecipientProvider']]
       )
       throw e
   }
}
```

## 2. jenkins在k8s中案例

```shell
def label = "mypod-${UUID.randomUUID().toString()}"
podTemplate(label: label, containers: [
    containerTemplate(name: 'jnlp', image: 'hexun/jnlp-slave-maven:apline', ttyEnabled: true, alwaysPullImage: false,args: '${computer.jnlpmac} ${computer.name}'),
  ],
  volumes: [
    hostPathVolume(mountPath: '/var/run/docker.sock', hostPath: '/var/run/docker.sock'),
    hostPathVolume(mountPath: '/usr/bin/docker', hostPath: '/bin/docker')
  ],) {

    node(label) {
        def mvnHome = '/usr/share/maven'
        def DOCKER_REGISTRY_USER = 'admin'
        def DOCKER_REGISTRY_PSWD = 'Harbor12345'
        def DOCKER_REGISTRY_ADRESS = 'docker-image.ops.yws.bj2.yongche.com'

        stage('init sys env') {
            container('jnlp') {
                  sh '''
                     echo -e "nameserver 10.254.0.2\nsearch default.svc.cluster.local svc.cluster.local cluster.local\noptions ndots:2 edns0" | sudo tee /etc/resolv.conf
                     cat /etc/resolv.conf
                  '''
            }  
        }

        stage('checkout & build') {
            // Get some code from a GitLab repository
            git credentialsId: 'gitlab', url: 'http://172.17.80.26/blog/zrlog.git'

            // Run the maven build
            if (isUnix()) {
              sh "'${mvnHome}/bin/mvn' clean install"
              } else {
              bat(/"${mvnHome}\bin\mvn" clean install/)
              }
        }

        stage('build docker images') {
            // Get git commit number
            def commitID = sh(returnStdout: true, script: 'git rev-parse HEAD').take(8)
            // build docker images
            sh "sudo docker login -u ${DOCKER_REGISTRY_USER} -p ${DOCKER_REGISTRY_PSWD} ${DOCKER_REGISTRY_ADRESS}"
            sh "sudo docker build -t ${DOCKER_REGISTRY_ADRESS}/test/zrlog:${commitID} ."
            sh "sudo docker push ${DOCKER_REGISTRY_ADRESS}/test/zrlog:${commitID}"
            sh "sed -i 's/<commitID>/${commitID}/g' zrlog.yml"
        }

        stage('deploy k8s cluster') {
            sh '''
            kubectl apply -f zrlog.yml
            '''
        }
   }
}
```

如果你将jenkins slave部署到k8s集群中，需要进行如下授权：

```shell
$ kubectl create clusterrolebinding jenkins-cicd --clusterrole cluster-admin --serviceaccount=jenkins-cicd:default
```

配置私有仓库harbor的secret

```shell
kubectl create secret docker-registry registry-secret \
    --docker-server=docker-image.ops.yws.bj2.yongche.com --docker-username=admin \
    --docker-password=Harbor12345 --docker-email=yangsheng@yongche.com
```

查看信息确定是否生成

```shell
$ kubectl get secrets registry-secret
NAME              TYPE                             DATA      AGE
registry-secret   kubernetes.io/dockerconfigjson   1         5m
```
