'''
    This module provides AppRules Class, which defines a set of Rules or Steps
    within a given process.  Defines data for tracking status of the rules.

    This needs more work, but I like the basic concept of introducting a kind of
    rules engine / service orchestrator control module. Would probably be interesting
    to add in the concept of alternative paths, based on evaluation of some criteria,
    even random(-ish).
'''
# Python packages
import sys
import os
# Local packages
sys.path.append('app')
import main
from main import utils

class AppRules:
  '''
    Defines the steps for parsing the designated POM.
  '''
  def __init__(self, T):
    '''
        Instantiate AppRules object.

        params
            T:  AppText object
    '''
    self.RuleSet = {'build_app':{0:T.Texts['pomGet'],
                                 1:T.Texts['pomRead'],
                                 2:T.Texts['pomEval'],
                                 3:T.Texts['buildDirectories'],
                                 4:T.Texts['buildControls'],
                                 5:T.Texts['checkPackages'],
                                 6:T.Texts['checkServices'],
                                 7:T.Texts['buildDone']}}
    self.RuleList = {}
    self.RuleTxt = ''
    self.RuleIdx = 0
    self.LastRuleIdx = len(self.RuleSet['build_app']) - 1
    self.ProcessCompleted = False
    self.ProcessLastStep = False

  def ResetRules(self):
    '''
        (Re-)Initialize values in the AppRules object.
    '''
    self.RuleIdx = 0
    self.RuleTxt = self.RuleList[self.RuleIdx]
    self.ProcessCompleted = False
    self.ProcessLastStep = False

  def SetRuleList(self, setname):
      '''
        Identify which set of rules to use,
        param setname is the set-level index from self.RuleSet.
      '''
      self.RuleList = self.RuleSet[setname]

  def NextRule(self):
    '''
        Advance to the next rule.
    '''
    # Reset if index is less than zero
    if self.RuleIdx < 0:
        self.ResetRules()
    # If step is at the last rule, leave it there
    if self.RuleIdx == self.LastRuleIdx:
        self.ProcessLastStep = True
    # If step is beyond end of list, then reset idx to final rule
    elif self.RuleIdx > self.LastRuleIdx:
        self.ProcessCompleted = True
        self.RuleIdx = self.LastRuleIdx
	# Advance to the next rule
    else:
		self.RuleIdx += 1
	# Set text for the current rule
    self.RuleTxt = self.RuleList[self.RuleIdx]
