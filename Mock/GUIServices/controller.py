#!/usr/bin/python3.9
"""
:module:    controller.py
:kv:        controller.kv
:sh:        controller.sh

:author:    GM (genuinemerit @ pm.me)

Prototype Kivy GUI for a GUIServices module that functions
as the Service Activator and Deactivator. This module starts
and stops the services for the BoW app(s). It reads information
from Redis DB 1 "Schema" to identify:
- Topics
- Plans
- Services
- Schemas

At least initially, maybe it simply runs the bash shell script
"control_servers.sh" to start and stop the services.
But would be nice to pythonize it. Instead of putting all the
logic in a shell script, it would be nice to put it in python
as much as possible.


It works in synch with a .kv file. The "App" class is
named "ControllerApp", so the .kv file is "controller.kv".
The .kv file is located in the same directory as this file.

Widgets:
- Labels --> one for each each server
- Text --> to route stdout and stderr
- StartButton  --> to fire up all servers
- KillButton   --> so stop all servers
- InfoButton   --> to show info about the services
- ControlStation --> to whatever else I need, e.g.,
                     to play around with timed updates, logs maybe

App:
- ControllerApp -->
  Manage a loop by calling ControlStation update() method
  every "frame".
"""
import kivy                          # type: ignore
import subprocess as shl

from kivy.app import App             # type: ignore
from kivy.uix.widget import Widget   # type: ignore
from kivy.uix.button import Button   # type: ignore
# from kivy.uix.floatlayout import FloatLayout   # type: ignore  # noqa: F401

kivy.require('2.0.0')


class Shell(object):
    """
    Shell class to run shell commands.
    """

    @classmethod
    def run_cmd(cls, p_cmd: list) -> tuple:
        """Execute a shell command.
        Only tested with `bash` shell under POSIX:Linux.
        Don't know if it will work properly on MacOS or Windows
        or with other shells.
        Args:
            p_cmd (list) shell command as a string in a list
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


class ControllerLayout(Widget):
    pass


class ControllerApp(App):
    """
    @DEV
    - Add a call to show running jobs.
    - Figure out why the bash call isn't really working.
    - Figure out how to get the stdout and stderr from bash.
    - Keep reading up on using kivy; set up widgets using .kv file.
    """

    def build(self):
        ba = {
            "col": (.8, .9, 0, 1),
            "fs": 24,
            "sz": (200, 100)}
        parent = Widget()
        other_stuff = ControllerLayout()
        start_btn = Button(
            text='Start Services',
            # pos=(0, 100),
            pos=(0, 500),
            color=ba["col"], font_size=ba["fs"],
            size=ba["sz"])
        stop_btn = Button(
            text='Kill Services',
            pos=(200, 500),
            color=ba["col"], font_size=ba["fs"],
            size=ba["sz"])
        start_btn.bind(on_release=self.start_services)
        stop_btn.bind(on_release=self.stop_services)
        parent.add_widget(other_stuff)
        parent.add_widget(start_btn)
        parent.add_widget(stop_btn)
        return parent

    def start_services(self, obj):
        """Returns true but doesn't seem to do anything unless I use exec_bash,
           which works. However, the python app freezes while  bash script is
           running. And I'm not getting stdout, stderr.
           Next, I need to:
           - Run the bash script in a separate process, that is, in background.
           - Read the stdout and stderr from the bash script. Figure out how.
           - Or, use additional system/OS calls to gather the status on  jobs.
        """
        cmd_result = SH.exec_bash(["bash controller.sh --run"])
        print(cmd_result)

    def stop_services(self, obj):
        cmd_result = SH.exec_bash(["bash controller.sh --kill"])
        print(cmd_result)


if __name__ == '__main__':
    SH = Shell()
    ControllerApp().run()
