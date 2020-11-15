# ansible-devops
基于 django + ansible + celery 的自动化运维实现方案：
- 前端，使用Nginx做代理转发，前端开发使用了Bootstrap的一些组件
- 后端，使用Django处理服务逻辑，调用Ansible Api进行playbook的执行和任务的处理，处理的结果使用Redis临时存储，使用Celery进行异步任务处理，同时Redis为Celery的Broker，
使用MySQL进行最终结果的存储
