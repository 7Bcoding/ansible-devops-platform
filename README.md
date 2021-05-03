# ansible-devops-platform
## 基于 django + ansible + celery 的自动化运维实现方案：
* 前端，使用Nginx做代理转发，前端开发使用了Bootstrap的一些组件
* 后端，使用Django处理服务逻辑，调用Ansible Api进行playbook的执行和任务的处理，处理的结果使用Redis临时存储，使用Celery进行异步任务处理，同时Redis为Celery的Broker，
使用MySQL进行最终结果的存储
![image](https://user-images.githubusercontent.com/17037398/116837560-83213800-abfd-11eb-8e9c-38fd1d466eeb.png)
## 运行方式：
-- 启动django：python3 manage.py runserver 0.0.0.0:8080
-- 启动celery：celery multi start 3 -A myCelery -l info -c 4 --pidfile=tmp/celery_%n.pid -f logs/celery.log（启动 3 个 worker，每个 worker 启动 4 个子进程）
-- 启动flower: celery flower -A test_celery --port=8080
