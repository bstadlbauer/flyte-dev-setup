from flytekit import task, workflow


@task
def do_nothing_task():
    raise ValueError()


@workflow
def do_nothing_workflow():
    do_nothing_task()
