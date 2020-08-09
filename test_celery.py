# 最简化构建一个 celery 应用，指定了 broker 和 backend
from celery import Celery
# 定义 broker 和 backend，分别为任务中间人和结果保存路径
BROKER = "redis://:@127.0.0.1:6379/3"
BACKEND = "redis://:@127.0.0.1:6379/4"

app = Celery("tasks",broker=BROKER,backend=BACKEND,)
app.conf.task_send_sent_event = True
app.conf.worker_send_task_events = True

from celery.schedules import crontab
from datetime import timedelta
app.conf.timezone = 'Asia/Shanghai'
app.conf.beat_schedule = {
    'task_every_30_seconds': {
        'task': 'test_celery.add',  # 调用 add 任务
        'schedule': timedelta(seconds=5),   # 每隔 5 秒执行一次
        'args': (23,  56)  # 作为参数传递进去
    },
    'task_every_min': {
        'task': 'test_celery.add',
        'schedule': crontab(minute='*'),    # 每分钟执行一次
        'args': (24, 57)
    }
}
from celery import Task
class MyTask(Task):
    abstract = True

    # 任务返回结果后执行
    def after_return(self, *args, **kwargs):
        print('任务返回结果: {0!r}'.format(self.request))

    # 任务执行失败是调用
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print('任务执行失败')


    # 任务重试时调用
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        print('任务正在重试')


    # 任务成功时调用
    def on_success(self, retval, task_id, args, kwargs):
        print('任务执行成功')

from celery.result import AsyncResult
@app.task
def error_handler(uuid):
    result = AsyncResult(uuid)
    print('任务 %s 执行失败raised exception: ' % uuid)

# 定义一个任务，名字为 add
@app.task(bind=True,base=MyTask)
def add(self, x, y):
    c = x + y
    print('计算结果为： %d ' % c)
    return c

@app.task(bind=True,max_retries=3)  # 最大重试 3 次
def test_retry(self):
    print('执行 Celery 重试')
    raise self.retry(countdown=1) # 1 秒后执行重试

@app.task(bind=True)
def test_fail(self):
    print('执行 Celery 失败')
    raise RuntimeError('测试 celery 失败')