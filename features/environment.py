# -*- coding: UTF-8 -*-
import subprocess
import os
import logging
import re


def run(command):
    # TODO: Rewrite me with ansible and move me to common_steps
    try:
        return subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        print("Output: %s" % e.output)
        raise e


def before_all(context):
    # Save run proc as context.run
    context.run = run


# TODO move me to common steps
def cleanup(context):
    # Read container cid (if available)
    if not os.path.exists(context.cid_file):
        return

    cid = None
    with open(context.cid_file, "r") as f:
        cid = f.read().strip()

    try:
        # Cleanup previous container
        run("docker stop %s" % cid)
        exit_status = run("docker inspect -f '{{.State.ExitCode}}' %s" % cid)
        if exit_status != "0":
            logging.debug(run("docker logs %s" % cid))
    finally:
        run("docker kill %s" % cid)
        run("docker rm %s" % cid)
        os.remove(context.cid_file)


def before_scenario(context, scenario):
    # TODO: Move me to a function and run it from example's before_scenario

    # Stop container and remove it
    # Container name is stored in context.userdata.image
    # Can be redefined in runtime via 'behave -D image="woot"'
    # If its not specified it will be built

    try:
        if 'image' not in context.config.userdata:
            raise Exception("Please specify image to test: behave -D=image=test")
        context.image = context.config.userdata['image']
        # Make sure we generate nice name here (for images like openshift/postgresql-92-centos7)
        cid_file_name = re.sub(r'\W+', '', context.image)
        context.cid_file = "/tmp/%s.cid" % cid_file_name
        cleanup(context)
    except Exception as e:
        print("before_scenario: exception %s" % str(e))


def after_scenario(context, scenario):
    # TODO: Move me to a function and run it from example's before_scenario

    # Store scenario logs
    try:
        if not getattr(context, "cid", None):
            return
        if scenario.status == 'failed':
            print(run("docker logs %s" % context.cid))
        cleanup(context)
    except Exception as e:
        print("after_scenario: exception %s" % str(e))
