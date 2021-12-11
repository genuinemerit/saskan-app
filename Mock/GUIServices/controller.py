#!/usr/bin/python3.9
"""
:module:    controller.py

:author:    GM (genuinemerit @ pm.me)

Prototype python replacement for the controller.sh script.
"""
import argparse
import subprocess as shl
import time
from pprint import pprint as pp


class Shell(object):
    """
    Shell class to run shell commands.
    """

    @classmethod
    def run_cmd(cls, p_cmd: str) -> tuple:
        """Execute a shell command.
        Only tested with `bash` shell under POSIX:Linux.
        Don't know if it will work properly on MacOS or Windows
        or with other shells.
        Args:
            p_cmd (str) shell command as a string
        Returns:
            tuple: (success/failure: bool, result: bytes)
        """
        cmd_rc = False
        cmd_result = b''   # Stores bytes

        if p_cmd == "" or p_cmd is None:
            cmd_rc = False
        else:
            # shell=True means cmd param contains a regular cmd string
            shell = shl.Popen(p_cmd, shell=True, stdin=shl.PIPE,
                              stdout=shl.PIPE, stderr=shl.STDOUT)
            cmd_result, _ = shell.communicate()
            if 'failure'.encode('utf-8') in cmd_result\
                    or 'fatal'.encode('utf-8') in cmd_result:
                cmd_rc = False
            else:
                cmd_rc = True
        return (cmd_rc, cmd_result)

    def exec_bash(self, p_cmd_list: list) -> str:
        """Run a series of one or more OS (bash) commands.
        Args:
            p_cmd_list (list) of strings formatted correctly as OS commands
            for use in call to run_cmd/1
        Returns:
            string: decoded message from execution of last command in list
        """
        for cmd in p_cmd_list:
            _, result = self.run_cmd(cmd)
            result = result.decode('utf-8').strip()
        return result


class ControllerApp(object):
    """
    @DEV
    - Add a call to show running jobs.
    - Figure out why the bash call isn't really working.
    - Figure out how to get the stdout and stderr from bash.
    - Keep reading up on using kivy; set up widgets using .kv file.

    Now its works but still gets "stuck" when the services are running,
    even though the bash job is submitted in background.
    If I kill the python program, the services still run fine and the
    kill button works fine too if I bring the python program back up.

    I think I need to get away from using bash altogether?
    Easy enough to run a python script from another python script.

    Sounds like "harvesting" from stdout and stderr is not a recommended
    practice either. That's OK. It's why I have the monitoring services
    architecture on the sketchpad.

    Kind of wondering if using asyncio with Popen would work?

    May want to use bash to start the services and use the python script/GUI
    only for monitoring and killing.

    This works beautifully from the command line:
        bash controller.sh -r &>> /home/dave/saskan/log/controller.log &

    But keep in mind that harvesting stdout and stderr interactively is a
    bad idea. May want to write stderr to log, but stdout to /dev/null,
    and rely on the "wiretap" function instead.
    """
    def __init__(self, **kwargs):
        self.logfile = "/home/dave/saskan/log/controller.log"
        self.controller_cmd = "python3.9 -u {} &"

    def start_services(self, args):
        """This works but...
           - I get the same problem as launching the bash script, i.e.,
             python controller module gets 'stuck' waiting for completion.
           - Also, eventually want to pull the config data from redis.
        """
        pp((args.jobdir))
        pp((args.jobs))
        for job in args.jobs:
            print(job)
            cmd = "python3.9 -u {}/{} &".format(args.jobdir, job)
            pp((cmd))
            cmd_rc, cmd_result = SH.run_cmd(cmd)
            pp(((cmd_rc, cmd_result)))
            time.sleep(0.5)

    def stop_services(self, args):
        # cmd_result = SH.exec_bash(["bash controller.sh --kill"])
        # print(cmd_result)
        cmd_rc, cmd_result = SH.run_cmd(
            self.controller_cmd.format("kill", self.logfile))
        pp(((cmd_rc, cmd_result)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    jobs = ["redis_server.py",
            "redis_response.py", "redis_response.py",
            "redis_request.py"]
    parser.add_argument('--jobdir', default='../IOServices')
    parser.add_argument('--jobs', default=jobs)
    try:
        SH = Shell()
        CA = ControllerApp()
        CA.start_services(parser.parse_args())
    except KeyboardInterrupt:
        print('Bye!')
