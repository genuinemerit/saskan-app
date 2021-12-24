#!/usr/bin/python3.9
"""
:module:    controller_gui.py
:kv:        controller.kv
:sh:        controller.sh

:author:    GM (genuinemerit @ pm.me)

Kivy Controller GUI.
A Service Monitor and Deactivator component.

This module shows what services are running and can stop them.
To start up services, for now use the bash controller.sh.

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
- Keep working on integrating this with the Admin and Monitor GUI's,
  and with the bow_tap wiretap component, and their related services,
  functions, and Redis namespaces.
"""
import time
from pprint import pprint as pp

import kivy  # type: ignore
from kivy.app import App  # type: ignore
from kivy.uix.button import Button  # type: ignore
from kivy.uix.widget import Widget  # type: ignore

from BowQuiver.BowQuiver.saskan_texts import SaskanTexts  # type: ignore
from BowQuiver.BowQuiver.utils import Utils  # type: ignore

TX = SaskanTexts()
UT = Utils()

kivy.require('2.0.0')


class ControllerShell(object):
    """Run Controller-related commands."""

    def check_running_services(self,
                               p_service_nm: str) -> tuple:
        """Check if a service is running.
        Args:
            p_service_nm (str) name of service to check
        Returns:
            tuple: (is_running: bool, msg: str)
        """
        cmd = f"ps -ef | grep -v grep | grep {p_service_nm}"
        _, result = UT.run_cmd(cmd)
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
            _, pid_count = UT.run_cmd(cmd)
            if (int(pid_count.strip("\n")) > 0):
                cmd = f"ps -ef | grep -v grep | grep {server_nm} | "
                cmd += "awk '{print $2}'"
                _, pid_num = UT.run_cmd(cmd)
                pid_num = pid_num.strip("\n")
                cmd = f"kill -9 {pid_num}"
                rc, result = UT.run_cmd(cmd)
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


class ControllerApp(App):
    """
    @DEV
    - Keep reading up on using kivy. Set up widgets using .kv file.
    - Merge this GUI with Admin and Monitor GUI's.
    """
    def __init__(self, **kwargs):
        super(ControllerApp, self).__init__(**kwargs)
        self.title = "Controller"
        self.CS = ControllerShell()

    def info_redis(self, *args):
        """Use python functions to get info on running jobs."""
        srv_nm = f"{TX.res.jobs_path}/redis"
        is_running, msg = self.CS.check_running_services(srv_nm)
        pp((is_running, msg))

    def stop_redis(self, *args):
        """Use python functions to kill running jobs."""
        srv_nm = f"{TX.res.jobs_path}/redis"
        is_stopped, msg = self.CS.stop_running_services(srv_nm)
        pp((is_stopped, msg))

    def build(self):
        btn_col = (.8, .9, 0, 1)
        btn_fs = 18
        btn_sz = (250, 75)
        parent = Widget()

        info_btn = Button(
            text=TX.res.btn_redis_info[1],
            pos=(0, 500),
            color=btn_col,
            font_size=btn_fs,
            size=btn_sz)
        info_btn.bind(on_release=self.info_redis())
        parent.add_widget(info_btn)

        stop_btn = Button(
            text=TX.res.btn_redis_kill[1],
            pos=(255, 500),
            color=btn_col,
            font_size=btn_fs,
            size=btn_sz)
        stop_btn.bind(on_release=self.stop_redis)
        parent.add_widget(stop_btn)

        return parent


if __name__ == '__main__':
    ControllerApp().run()
