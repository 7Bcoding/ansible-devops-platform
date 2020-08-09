from test_celery import *

i = app.control.inspect()

print('\33[31mCelery 获取节点: %s\33[0m' % i.active())
print('\33[32mCelery 活跃队列:%s\33[0m' % i.active_queues())
print('\33[33mCelery 状态监测:%s \33[0m' % i.ping())

# 添加一个延时任务
add.apply_async((2,3), countdown=5)

print('\33[31mCelery 延时任务：%s\33[0m' % i.scheduled())
print('\33[32mCelery 状态:%s\33[0m' % i.stats())