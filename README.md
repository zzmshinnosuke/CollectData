# CollectData
两类人员项目，通过安卓客户端数据采集上传，服务器端数据接收保存。以及服务器端进行异常检测的接口

# setting
需要配置merge.py中的四个数据库的参数
ip="ip"
port=3306
user="database user"
passwd="password"

## 客户端
GetInfo 不是我做的

## 服务器端
基于django框架  
启动：`python manage.py runserver 0.0.0.0:9000`  
在/CollectData/urls.py 配置接口名称
在/web/views.py 中编写接口处理代码

### 服务器端接收数据接口
IP:9000/LogInfo 登录

### 服务器端异常检测接口
IP:9000/Behavior  

### 数据库mysql
需要创建一个数据库 justice
创建四个表：GPS、PhoneBook、PhoneCall、SMS

20210408: 两类人员项目重新弄了一下，有些错误。（1）数据库用户权限有些问题，没有update权限。计算gps数据时出错，pandas中的一个函数as_matrix出错了，新版本的pandas不支持这个函数了，又重新装了一下可以了
