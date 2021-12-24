#!/usr/bin/python3.9
"""
:module:    controller_gui.py
:kv:        controller.kv,
            controller_display.kv,
            controller_options.kv,
            controller_status.kv,
            controller_toolbox.kv,

:author:    GM (genuinemerit @ pm.me)

BoW Saskan Controller GUI. (prototype)

This app is a Service Activator/Deactivator
and monitor for Saskan services.

App:
- ControllerApp       --> main app
"""
from pprint import pprint as pp  # type: ignore

import kivy  # type: ignore
from kivy.app import App  # type: ignore
from kivy.lang import Builder  # type: ignore
from kivy.uix.anchorlayout import AnchorLayout  # type: ignore

from BowQuiver.BowQuiver.saskan_texts import SaskanTexts  # type: ignore
from controller_shell import ControllerShell  # type: ignore

kivy.require('2.0.0')

Builder.load_file('controller_display.kv')
Builder.load_file('controller_options.kv')
Builder.load_file('controller_status.kv')
Builder.load_file('controller_toolbox.kv')

TX = SaskanTexts()


class ControllerManager(AnchorLayout):
    """
    The main ControllerManager class.
    """
    pass


class ControllerApp(App):
    """
    The main ControllerApp class.
    """
    def __init__(self, **kwargs):
        super(ControllerApp, self).__init__(**kwargs)
        self.CS = ControllerShell()

    def stop_redis(self, instance):
        """Use python functions to kill running RedisIO jobs."""
        srv_nm = f"{TX.res.jobs_path}/redis"
        is_stopped, msg = self.CS.stop_running_services(srv_nm)
        pp((is_stopped, msg))

    def build(self):
        """
        Build the main app.
        """
        return ControllerManager()


if __name__ == '__main__':
    ControllerApp().run()
