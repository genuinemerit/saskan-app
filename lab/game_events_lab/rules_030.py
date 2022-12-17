#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module provides a Class which defines sets of Rules or Steps
within a given process.  Defines data for tracking status of the rules.
"""
# Python modules
from pprint import pprint as pp

# FUNCTIONS
#       None

# CLASS
# =========================
class Steps(object):
    """
    Defines the steps for parsing the designated list.
    """
    def __init__(self, ruletxts):
        """
        Instantiate new steps object.

        Args:
            ruletxts:  app texts dict for selected set of rules
        """
        # print "ruletxts:/n"
        # pp(ruletxts)        
        self.rule_meta = {}
        self.rule_data = {}
        self.rule_num = {}
        self.steps_stat = ''
        self.step_msg = ''
        self.step_values = {}
        
        self.rule_meta = ruletxts["meta"]
        self.rule_data = ruletxts["text"]
        # print "self_rule_meta:/n"
        # pp(self.rule_meta)       
        # print "self_rule_data:/n"
        # pp(self.rule_data)
        self.rule_num["this"] = 0
        self.rule_num["max"] = len(self.rule_data) - 1
        self.steps_stat = "first"
        self.step_msg = self.rule_data[self.rule_num["this"]]
        # print "self_rule_num:/n"
        # pp(self.rule_num)
        self.step_values= {idx:{}for idx in range(self.rule_num["max"])}
        # print "self_step_values:/n"
        # pp(self.step_values)

    def get_step(self):
        """
        Returns:
            Dict: current step number, status, message
        """
        return {"num": self.rule_num["this"],
                "max": self.rule_num["max"],
                "stat": self.steps_stat,
                "msg": self.step_msg}

    def set_value(self, pnum, pkey, pvalue):
        """
        Assign a value to be stored with a step number.
        Typically this would be the result of a computation for that step.

        Args:
            pnum:       Rule number, acts as index to the stored value
            pkey:       Type of value to be stored, used as a sub-index
            pvalue:     Value associated with the pkey
        """
        self.step_values[pnum][pkey] = pvalue

    def next_rule(self):
        """
        Advance to the next rule.
        """
        # Reset if index is less than zero
        self.rule_num["this"] = 0 if self.rule_num["this"] < 0 \
                                  else self.rule_num["this"]
        # Advance to the next step
        self.rule_num["this"] += 1
        self.steps_stat = "next"
        # See if we are finished with the process
        if self.rule_num["this"] > self.rule_num["max"]:
            self.step_msg = self.rule_data['setDone']
            self.steps_stat = "done"
        else:
            self.step_msg = self.rule_data[self.rule_num["this"]]
            if self.rule_num["this"] == self.rule_num["max"]:
                self.steps_stat = "last"
