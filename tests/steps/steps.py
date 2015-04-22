# -*- coding: UTF-8 -*-
from behave import step, when, then, given
import subprocess
from time import sleep


@step(u'Docker container is started with params "{params}"')
def container_started(context, params=''):
    # TODO: allow tables here
    # A nice candidate for common steps
    context.job = context.run('docker run -d --cidfile %s %s %s' % (context.cid_file, params, context.image))
    context.cid = open(context.cid_file).read().strip()


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

    # Get container IP
    context.ip = context.run("docker inspect --format='{{.NetworkSettings.IPAddress}}' %s" % context.cid).strip()

    context.execute_steps(u'* port 5432 is open')

    for attempts in xrange(0, 5):
        try:
            context.run('docker run --rm -e PGPASSWORD="%s" %s psql postgresql://%s@%s:5432/%s <<< "SELECT 1;"' % (
                password, context.image, user, context.ip, db))
            return
        except subprocess.CalledProcessError:
            # If  negative part was set, then we expect a bad code
            # This enables steps like "can not be established"
            if action != 'can':
                return
            sleep(5)

    raise Exception("Failed to connect to postgresql")


@step(u'port {port:d} is open')
@step(u'port {port:d} is {negative} open')
def port_open(context, port, negative=False):
    # Get container IP
    context.ip = context.run("docker inspect --format='{{.NetworkSettings.IPAddress}}' %s" % context.cid).strip()

    for attempts in xrange(0, 5):
        try:
            print(context.run('nc -w5 %s %s < /dev/null' % (context.ip, port)))
            return
        except subprocess.CalledProcessError:
            # If  negative part was set, then we expect a bad code
            # This enables steps like "can not be established"
            if negative:
                return
            sleep(5)

    raise Exception("Failed to connect to port %s" % port)
