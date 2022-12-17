#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Map Handler Service
:module:    map_msg_handler
:classes:   ManageQueues, ScanRequests, ScanResults
:author:    genuinemerit <dave@davidstitt.solutions>

Back-end / middle-ware daemon.

Daemon job devoted to handling/processing messaging queues.
Scans the message queue for pending messages.
Processes them in order in which they arrived.

Puts a LOCK on the request queue when it is modifying that queue.
Writes in-flight message to a process queue.
Writes results (data provided from map_svg_maker) to result queue.
All queues are in-memory files ("/dev/shm") for now. 
All are pure JSON.

It reads messages which were written to the request queue by map_msg_service.
It makes direct calls to map_svg_maker to process them and get results.

To-Do:
1) Include signatures in the results packages so that only requesters can subscribe them.
2) Add logic to clean up the results queue.. Remove/log items after they have been there a while.
3) Support ability to broadcast a message... Publish a result with an "open" signature.
4) Parameterize all the queue names further so that we can easily run parallel testing.

# pylint: disable=R0903

"""
from pprint import pprint as pp           # pylint: disable=W0611
import time
import json
import sys
from os import path
from bow_func_basic import FuncBasic
from map_svg_maker import MapMaker
FB = FuncBasic()
MM = MapMaker()

PAUSE = .200     # 200 milliseconds
LOOPER = True    # Continuous loop mode  (False = execute loop only once mode)

class ManageQueues():
    """ Register the queues.  
        To Do: Add monitoring/capacity checks.  Backup. 
    """
    rqst_q = None
    proc_q = None
    rslt_q = None

    def __init__(self):
        """ Init the class. """
        self.rqst_q = "/dev/shm/rqst.que"
        self.proc_q = "/dev/shm/proc.que"
        self.rslt_q = "/dev/shm/rslt.que"

class ScanRequests():
    """ Scan the request queue for pending messages """
    msg = None

    def __init__(self):
        """ Init the class. """
        self.msg = dict()

    def scan_request_q(self):
        """ Scan the request queue.
            There are queue-like structures in python I could use instead of JSON files.
            It just feels neat, clean to do it in JSON & plain old files first.
        """
        rqst_d = dict()
        if path.isfile(MQ.rqst_q):
            with open(MQ.rqst_q, 'r') as rqst_f:
                rqst_j = rqst_f.read()
                if rqst_j not in ['', None, '[]']:
                    rqst_d = json.loads(rqst_j)
                rqst_f.close()
            if rqst_d:
                # Put a lock on the queue
                FB.que_me('"LOCK"')
                # Pop the top request message. Sort (asc) by key values. Take the top key value.
                rqst_key = sorted(rqst_d.keys())[0]
                self.msg = rqst_d[rqst_key]
                self.msg['rqst_key'] = rqst_key
                # Persist popped message to process queue
                FB.que_me(json.dumps(self.msg), MQ.proc_q)
                # Remove popped message from request queue
                del rqst_d[rqst_key]
                # Rewrite the message queue sans in-process message
                # This removes the lock since it restores from a cache that did not have the LOCK
                with open(MQ.rqst_q, 'w') as rqst_f:
                    rqst_f.write(json.dumps(rqst_d))
                    rqst_f.close()
                # Don't need to call submit_request directly. The message will get picked up by
                #  scan of the in-process queue.

    def scan_process_q(self):
        """ Scan items in the In-Process queue.
            If something is in here, that means -- in all likelihood -- that a previous attempt to
            process it failed.  This scan is here to automatically catch up on re-tries.
        """
        proc_d = dict()
        if path.isfile(MQ.proc_q):
            with open(MQ.proc_q, 'r') as proc_f:
                proc_j = proc_f.read()
                if proc_j not in ['', None, '[]']:
                    proc_d = json.loads(proc_j)
                proc_f.close()
            if proc_d:
                # Pop the top in-process message. Sort (asc) by key values. Take the top key value.
                proc_key = sorted(proc_d.keys())[0]
                self.msg = proc_d[proc_key]
                self.msg['proc_key'] = proc_key
                # Remove it from the queue later, after a result message has been created.
                self.submit_request(proc_key)

    def submit_request(self, proc_key):
        """ Call MapMaker to update Catalog and generate SVG code 
            To Do: If I break up Catalog updates from SVG generation and Catalog queries, 
                    then may need to do multiple calls from here instead of only one.
        """
        call_nm = dict()
        call_nm = {'svg': MM.handle_svg,
                   'ref': MM.handle_ref,
                   'grp': MM.handle_grp,
                   'elm': MM.handle_elm,
                   'use': MM.handle_use,
                   'tgp': MM.handle_tgp,
                   'txt': MM.handle_txt,
                   'img': MM.handle_img}
        msgk = self.msg['msg']

        # Get result from MapMaker and write it to the result queue:
        rslt_msg_d = call_nm[msgk](self.msg)
        rslt_d = dict()
        if path.isfile(MQ.rslt_q):
            with open(MQ.rslt_q, 'r') as rsltf:
                rslt_j = rsltf.read()
                if rslt_j not in (None, ''):
                    rslt_d = json.loads(rslt_j)
                rsltf.close()
        rslt_d[rslt_msg_d['rqst_key']] = rslt_msg_d
        with open(MQ.rslt_q, 'w') as rsltf:
            rsltf.write(json.dumps(rslt_d))
            rsltf.close()

        # Remove the message from the process queue:
        proc_d = dict()
        with open(MQ.proc_q, 'r') as procf:
            proc_j = procf.read()
            if proc_j not in ['', None, '[]']:
                proc_d = json.loads(proc_j)
            procf.close()
        if proc_d:
            del proc_d[proc_key]
        # Rewrite the process queue.
        with open(MQ.proc_q, 'w') as procf:
            procf.write(json.dumps(proc_d))
            procf.close()

class ScanResults():
    """ Scan the results queue for expired/timed-out messages 
        To Do: Clean up the queue. Maybe send notifications/logs. 
        TO Do: Consider options for removing results once "the mail has been picked up". 
    """

    def __init__(self):
        """ Init the class. """
        pass

    def scan_results(self):
        """ Scan the result queue """
        pass


def main():
    """ Main loop. Check the queues every {PAUSE} microseconds. Ctrl-C to kill it.
        To Do:  Some self-care / self-healing. Kill/restart occasionally.
        To Do:  Throttle multiple instances based on load.  May be a good candidate for Docker?
        To Do:  Trottle config pause automatically based on.... ??
    """
    cmd = "ps -ef | grep map"
    FB.run_cmd(cmd)
    greprslt = FB.cmd_result.decode("utf-8")
    if greprslt.find('map_msg_service') < 0:
        raise Exception("Sorry, the map_msg_service must be running.")
    else:
        print("Required dependency: map_msg_service is running.")
        if LOOPER:
            print("The pause between scans is set to [" + str(PAUSE) + "] seconds")
        else:
            print("The program loop will execute only once.")
        loop = True
        while loop:
            if path.isfile(MQ.rqst_q):
                SQ.scan_request_q()
            if path.isfile(MQ.proc_q):
                SQ.scan_process_q()
            if path.isfile(MQ.rslt_q):
                SR.scan_results()
            loop = LOOPER                # When set to False, will execute only once.
            time.sleep(PAUSE)

if __name__ == "__main__":
    # If no argument provided, the program executes the loop only once.
    # The argument represents seconds. For example, 100 microseconds = .1 or 0.1 or .100
    if len(sys.argv) > 1:
        PAUSE = float(sys.argv[1])
    else:
        LOOPER = False 
    MQ = ManageQueues()
    SQ = ScanRequests()
    SR = ScanResults()
    main()
