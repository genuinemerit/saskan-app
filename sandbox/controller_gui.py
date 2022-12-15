#!/usr/bin/python3.9
"""
:module:    controller_gui.py
:kv:        controller.kv,
            controller_display.kv,
            controller_options.kv,
            controller_status.kv,
            # controller_toolbox.kv,

:author:    GM (genuinemerit @ pm.me)

BoW Saskan Controller GUI. (prototype)

This app is a Service Activator/Deactivator
and monitor for Saskan services.

App:
- ControllerApp       --> main app

@DEV
- Having trouble understanding the Kivy/Python relationships.
- For example, seems like capturing the state of a toggle button
  should be easy. But it's not.  I'm not sure why. And I am not
  finding any clear-cut examples.
- I'm not sure how to get the state of a toggle button.
- Keep working on various prototypes and tutorials.
- At the same time, prototype a simpler version for this app.
- I have a way to get regular buttons working, so work with that.
- Also not making much sense of the Anchored Layouts. Don't know
  why it isn't putting my buttons in the right place (at top)
"""
from pprint import pprint as pp  # type: ignore

import kivy  # type: ignore
from kivy.app import App  # type: ignore
from kivy.lang import Builder  # type: ignore
from kivy.uix.anchorlayout import AnchorLayout  # type: ignore

from BowQuiver.saskan_texts import SaskanTexts  # type: ignore
from controller_shell import ControllerShell  # type: ignore

kivy.require('2.0.0')

Builder.load_file('controller_buttons.kv')
Builder.load_file('controller_status.kv')
Builder.load_file('controller_display.kv')

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
