# -*- coding: UTF-8 -*-
from behave import step, when, then, given
import subprocess
from time import sleep
from common_steps import common_docker_steps, common_connection_steps


@when(u'postgresql container is started')
def postgresql_container_is_started(context):
    # Read postgresql params from context var
    params = ''
    for param in context.postgresql:
        params += ' -e %s=%s' % (param, context.postgresql[param])
    context.execute_steps(u'* Docker container is started with params "%s"' % params)


@given(u'postgresql container param "{param}" is set to "{value}"')
def set_postgresql_params(context, param, value):
    if not hasattr(context, "postgresql"):
        context.postgresql = {}
    context.postgresql[param] = value


@then(u'postgresql connection can be established')
@then(u'postgresql connection can {action:w} be established')
@then(u'postgresql connection with parameters can be established')
@then(u'postgresql connection with parameters can {action:w} be established')
def postgresql_connect(context, action=False):
    if context.table:
        for row in context.table:
            context.postgresql[row['param']] = row['value']

    user = context.postgresql['POSTGRESQL_USER']
    password = context.postgresql['POSTGRESQL_PASSWORD']
    db = context.postgresql['POSTGRESQL_DATABASE']

    context.execute_steps(u'* port 5432 is open')

    for attempts in xrange(0, 5):
        try:
            context.run('docker run --rm -e PGPASSWORD="%s" %s psql postgresql://%s@%s:5432/%s <<< "SELECT 1;"' % (
                password, context.image, user, context.ip, db))
            return
        except AssertionError:
            # If  negative part was set, then we expect a bad code
            # This enables steps like "can not be established"
            if action != 'can':
                return
            sleep(5)

    raise Exception("Failed to connect to postgresql")
