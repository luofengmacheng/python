## 使用vscode进行python的远程开发

详细的步骤可以看vscode网站上的文档：[Remote Development using SSH](https://code.visualstudio.com/docs/remote/ssh#_getting-started)，这里只是对搭建过程进行总结。

### 1 准备工作

* 远程云主机，由于需要安装插件，因此需要能够链接外网
* 安装软件：git、vscode

### 2 安装步骤

* 安装vscode
* ssh配置：git中包含ssh，可以在git安装路径下的`usr\bin`中找到ssh程序，将该路径加入到path
* 云主机的免密登录：在本地执行`ssh-keygen`生成公钥和私钥，然后将私钥拷贝到云主机的`/root/.ssh/authorized_keys`，然后从windows中尝试`ssh root@you_cloud_ip`登录，如果直接登录则免密登录配置成功
* vscode插件安装：在插件菜单搜索`remote`，安装插件`Remote-SSH`
* vscode插件安装完成后可以打开左侧的`Remote-SSH`菜单，点击CONNECTIONS后面的配置按钮，选择要使用的ssh配置，在其中配置好云主机的信息：

```
Host XXX
    HostName you_cloud_ip
    User root
    Port 22
```

* 然后尝试链接，如果链接成功，则可以用菜单`File->Open Folder`打开目录，如果可以看到远程主机的目录，则说明远程环境配置成功
* 安装远程插件：在插件菜单安装python插件，然后`ctrl+shift+p`，搜索`Interpreter`选择python所在路径
* 然后进行远程开发测试
