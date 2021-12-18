#!/usr/bin/python3.9
"""
:module:    controller_gui.py
:kv:        controller.kv
:sh:        controller.sh

:author:    GM (genuinemerit @ pm.me)

Kivy Controller GUI.
A Service Monitor and Deactivator component.

This module shows what services are running and can stop them.
To start up services, use the bash controller.sh.

Want to integrate this with work done on an Admin GUI and related
services and Redis namespace 1 "Schema". That can tell us what
services are defined, even if they are not running.

Ideally, this should work in synch with a .kv file.
The "App" class is named "ControllerApp", so .kv file is "controller.kv".
The .kv file needs to be located in the same directory as this file.

Potential Widgets:
- Labels --> one for each each service
- Texts - -> to display info
- KillButton   --> to stop a service
- InfoButton   --> to show info about a service
- ControlStation --> whatever else I need, e.g.,
                     play around with timed updates, logs maybe,
                     refreshes based on a clock, etc.
App:
- ControllerApp -->
    - For now, this is the whole app (very prototypy! :D)
    - Maybe manage a loop, calling a ControlStation update() method

@DEV:
- In general, want to avoid having to call a bash shell script
- As much as possible, submit OS commands directly from this program
  or its sub-classes.
- Keep working on integrating this with the Admin and Monitor GUI's,
  and with the bow_tap wiretap component, and their related services,
  functions, and Redis namespaces.
- The Utils kind of class probably needs to be moved to bow-quiver.
"""
import kivy                          # type: ignore
# import os
import subprocess as shl
import time
from pprint import pprint as pp

from kivy.app import App             # type: ignore
from kivy.uix.widget import Widget   # type: ignore
from kivy.uix.button import Button   # type: ignore
# from kivy.uix.floatlayout import FloatLayout   # type: ignore  # noqa: F401

kivy.require('2.0.0')


class ControllerShell(object):
    """
    Shell class to run Controller-related commands.
    May want to move this to a separate file, or even to bow-quiver.
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
        return (cmd_rc, cmd_result.decode('utf-8'))

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

    def check_running_services(self,
                               p_service_nm: str) -> tuple:
        """Check if a service is running.
        Args:
            p_service_nm (str) name of service to check
        Returns:
            tuple: (is_running: bool, msg: str)
        """
        cmd = f"ps -ef | grep -v grep | grep {p_service_nm}"
        _, result = self.run_cmd(cmd)
        is_running = True if p_service_nm in result else False
        show_msg = f"\nLooked for services like *..{p_service_nm[-32:]}*"
        return (is_running, f"{show_msg}\n{result}")

    def stop_running_services(self,
                              p_service_nm: str) -> tuple:
        """Stop a service.
        Args:
            p_service_nm (str) name of service to stop
        Returns:
            tuple: (is_stopped: bool, msg: str)
        """
        server_nm = p_service_nm + "_server.py"
        is_running, msg = self.check_running_services(server_nm)
        if is_running:
            show_msg = f"\nAttempting to kill {p_service_nm}"
            cmd = f'ps -ef | grep -v grep | grep -c "{server_nm}"'
            _, pid_count = self.run_cmd(cmd)
            if (int(pid_count.strip("\n")) > 0):
                cmd = f"ps -ef | grep -v grep | grep {server_nm} | "
                cmd += "awk '{print $2}'"
                _, pid_num = self.run_cmd(cmd)
                pid_num = pid_num.strip("\n")
                cmd = f"kill -9 {pid_num}"
                rc, result = self.run_cmd(cmd)
                time.sleep(0.5)
        is_running, show_msg = self.check_running_services(server_nm)
        if is_running:
            is_stopped = False
            show_msg += "\nSomething may be awry."
            show_msg += "\nTry doing a kill using admin/controller.sh."
        else:
            is_stopped = True
            show_msg += f"\n{p_service_nm} stopped."
        return (is_stopped, show_msg)


class ControllerLayout(Widget):
    """For future development."""
    pass


class ControllerApp(App):
    """
    @DEV
    - Add a call to show running jobs.
    - Keep reading up on using kivy. Set up widgets using .kv file.
    - Merge this GUI with Admin and Monitor GUI's.
    - Move the ControllerShell class to a separate module.
    """
    def __init__(self, **kwargs):
        super(ControllerApp, self).__init__(**kwargs)
        self.admin_path = "/home/dave/Dropbox/Apps/BoW/bow-data-schema/admin"
        self.jobs_path =\
            "/home/dave/Dropbox/Apps/BoW/bow-data-schema/BowDataSchema"

    def build(self):
        ba = {
            "col": (.8, .9, 0, 1),
            "fs": 18,
            "sz": (250, 75)}
        parent = Widget()
        other_stuff = ControllerLayout()
        parent.add_widget(other_stuff)

        info_btn = Button(
            text='Redis Services Info',
            pos=(0, 500),
            color=ba["col"],
            font_size=ba["fs"],
            size=ba["sz"])
        info_btn.bind(on_release=self.info_redis)
        parent.add_widget(info_btn)

        stop_btn = Button(
            text='Kill Redis Services',
            pos=(255, 500),
            color=ba["col"],
            font_size=ba["fs"],
            size=ba["sz"])
        stop_btn.bind(on_release=self.stop_redis)
        parent.add_widget(stop_btn)

        return parent

    def info_redis(self, obj):
        """Use python functions to get info on running jobs.
        """
        srv_nm = f"{self.jobs_path}/IOServices/redis"
        is_running, msg = SH.check_running_services(srv_nm)
        pp((is_running, msg))

    def stop_redis(self, obj):
        """Use python functions to kill running jobs.
        """
        srv_nm = f"{self.jobs_path}/IOServices/redis"
        is_stopped, msg = SH.stop_running_services(srv_nm)
        pp((is_stopped, msg))


if __name__ == '__main__':
    SH = ControllerShell()
    ControllerApp().run()
