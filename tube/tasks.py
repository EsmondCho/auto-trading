from django.core.cache import cache
from tube.tube_manager import TubeManager
from celery import shared_task


@shared_task
def tube_process_manage():
    tm = TubeManager()
    tube_info = cache.get("tube_info")

    if tube_info is None or tube_info['step_now'] is 0:
        return False
    else:
        tube_id = tube_info['tube_id']
        step_now = tube_info['step_now']

    if step_now == 3:
        result = tm.stage2()
        if result:
            toggle_celery_checked(tube_id, 1)
            toggle_celery_checked(tube_id, 2)
            toggle_celery_checked(tube_id, 3)
            toggle_celery_checked(tube_id, 4)
            toggle_celery_checked(tube_id, 5)

    elif step_now == 5:
        result = tm.stage3()
        if result:
            toggle_celery_checked(tube_id, 6)

    elif step_now == 6:
        result = tm.stage4()
        if result:
            toggle_celery_checked(tube_id, 7)
            toggle_celery_checked(tube_id, 8)

    elif step_now == 8:
        result = tm.stage5()
        if result:
            toggle_celery_checked(tube_id, 9)

    elif step_now == 10:
        result = tm.stage6()
        if result:
            toggle_celery_checked(tube_id, 10)
            toggle_celery_checked(tube_id, 11)

    elif step_now == 11:
        result = tm.stage7()
        if result:
            toggle_celery_checked(tube_id, 12)
            toggle_celery_checked(tube_id, 13)

    elif step_now == 13:
        result = tm.stage8()
        if result:
            toggle_celery_checked(tube_id, 14)

    elif step_now == 14:
        result = tm.stage9()
        if result:
            toggle_celery_checked(tube_id, 15)
            toggle_celery_checked(tube_id, 16)

    elif step_now == 16:
        result = tm.stage10()
        if result:
            toggle_celery_checked(tube_id, 17)

    elif step_now == 17:
        result = tm.stage11()
        # if result:
        #     toggle_celery_checked(tube_id, 18)

    return True


def toggle_celery_checked(tube_id, step):
    key = tube_id + ":" + str(step)
    value = cache.get(key)
    if value is not None:
        if value['celery_checked'] is True:
            return True
        else:
            value['celery_checked'] = True
            cache.set(key, value, timeout=None)
    return True





