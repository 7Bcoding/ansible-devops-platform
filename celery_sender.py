import datetime
from myCelery import *


class AnsibleOpt:
    @staticmethod
    def ansible_playbook(playbook, extra_vars={}):
        tid = "AnsibleApiPlaybook-%s" % (datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
        # 通过调用Celery任务函数ansiblePlayBook，调用AnsiblePlaybookApi
        celeryTask = ansiblePlayBook.apply_async(
            (tid, playbook, extra_vars), )  # ansible 结果保持
        return {"playbook": playbook,
                "extra_vars": extra_vars,
                "tid": tid,
                "celeryTask": celeryTask.task_id,
                }

    @staticmethod
    def ansible_opt(groupName, tasks):
        tid = "AnsibleApiOpt-%s" % datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        # 通过调用Celery任务函数ansibleExec，调用AnsibleApi
        celeryTask = ansibleExec.delay(tid, groupName, tasks)
        return {'tid': tid, 'celeryTask': celeryTask.task_id, "groupName": groupName}


if __name__ == '__main__':
    extra_vars = {'content': '这个参数从外部传入'}
    tasks = [dict(action=dict(module='debug', args=dict(msg='{{ content}}')))]

    # api
    AnsibleOpt.ansible_opt('localhost', tasks)
    # playbook
    AnsibleOpt.ansible_playbook('test_debug.yml', extra_vars)
