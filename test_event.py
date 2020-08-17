from celery import Celery
import json
import time
from test_celery import app


# 设置运行 tasks 发送事件

def my_monitor(app):
    state = app.events.State()

    # 处理事件
    def announce_failed_tasks(event):
        state.event(event)
        # task name 仅与-received 事件一起发送，使用 state 跟踪该事件。
        task = state.tasks.get(event['uuid'])

        print('任务失败: %s[%s] %s' % (
            task.name, task.uuid, task.info(),))

    # 处理事件
    def announce_tasks_callback(event):
        print('任务状态：%s - %s - %s - %s' %
              (event.get('hostname'), event.get('type'), event.get('uuid'),
               time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(event.get('timestamp')))))

    # 处理 worker 事件
    def announce_worker(event):
        if event.get('type') == 'worker-heartbeat':
            print('心跳检测')
        elif event.get('type') == 'worker-offline':
            print('worker 下线：%s - %s - %s ' %
                  (event.get('hostname'), event.get('type'),
                   time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(event.get('timestamp')))))
        elif event.get('type') == 'worker-online':
            print('worker 上线：%s - %s - %s ' %
                  (event.get('hostname'), event.get('type'),
                   time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(event.get('timestamp')))))
        else:
            pass

    with app.connection() as connection:
        recv = app.events.Receiver(connection, handlers={
            # 将 task 事件交给对应的处理函数
            'task-failed': announce_failed_tasks,
            'task-succeeded': announce_tasks_callback,
            'task-received': announce_tasks_callback,
            'task-revoked': announce_tasks_callback,
            'task-retried': announce_tasks_callback,

            # 将 worker 事件交给对应的处理函数
            'worker-online': announce_worker,
            'worker-offline': announce_worker,
        })
        recv.capture(limit=None, timeout=None, wakeup=True)


if __name__ == '__main__':
    my_monitor(app)
