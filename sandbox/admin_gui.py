#!/usr/bin/python3.9
"""
:module:    admin_gui.py
:kv:        admin.kv,
            toolbox.kv,
            displayspace.kv,
            adminoptions.kv,
            statusdisplay.kv

:author:    GM (genuinemerit @ pm.me)

BoW Saskan App Admin GUI. (prototype)

This app manages Redis Namespace #1 "Schema",
which is a Message Schema Store.

It also configures the Message Expiration settings
for Redis Namespace #3 "Log" and #4 "Monitor".

The "Schema" namespace holds 4 main types of entities, or record-types:
1) Topics   --> Categories of communication hanlded on a channel.
2) Plans    --> Set of services available on a topic.
3) Services --> Sets of request/response, or publish/subscribe,
   or other command/document message pairings in a plan.
4) Schema   --> Acceptable format of a particular message.

The Redis records use a format similar to -- but not exactly the same as --
the Avro schema format, a JSON-like format. Each record has a elements grouped
into keys, values and audit attributes.  Formats for the sub-records are the
same within each record type. In the "Schema" namespace, all of the records
define formats or configurations supporting the overall BoW message system.

Potential Kivy Objects:
- toolbox        --> with buttons
- displayspace   --> to display info, possibly graphically
- adminoptions   --> state and other controls
- statusdisplay  --> to display texts

App:
- AdminApp       --> main app

@DEV
- Initial prototype based on tutorial for "comicreator" in the book
_Kivy - Interactive Applications and Games in Python - Second Edition_
by Roberto Ulloa.
"""
import kivy                                     # type: ignore

from kivy.app import App                        # type: ignore
from kivy.lang import Builder                   # type: ignore
from kivy.uix.anchorlayout import AnchorLayout  # type: ignore

kivy.require('2.0.0')

Builder.load_file('admin_display.kv')
Builder.load_file('admin_options.kv')
Builder.load_file('admin_status.kv')
Builder.load_file('admin_toolbox.kv')


class AdminManager(AnchorLayout):
    """
    The main AdminManager class.
    """
    pass


class AdminApp(App):
    """
    The main AdminApp class.
    """
    def build(self):
        """
        Build the main app.
        """
        return AdminManager()


if __name__ == '__main__':
    AdminApp().run()
