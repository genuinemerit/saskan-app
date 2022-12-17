'''
    This module provides Functions which handle events triggered by forms
    or other sources of events.  For example, when a user clicks on a
    Submit button, what logic needs to occur, or when a GET event is
    triggered, what template is rendered.  As a program gets more complex
    it may be useful to separate submit (POST) event logic into a separate module
    from the logic to render GET events.

    Hmm. Yes, well, this is basically a continuation of the "handle a rule" idea,
    in this case as a reaction to a user event within a process. If I think of all
    this more in terms of messages, it is probably less likely to descend into a
    kind of hierarchical hellscape. :-)
'''

# flask modules
from flask import session, render_template

def set_pom(D):
    '''
        Refresh data values from session data
    '''
    D.ParentPomPath = session['ParentPomPath']
    D.ParentPomName = session['ParentPomName']

# Select POM file for Build
# ==========================================
def submit_select_pom(form, R, D):
    '''
        Handle a submit event (POST) on select/select.html
    '''
    # Assign form data to AppData structures
    D.ParentPomPath = form.BPomPath.data
    D.ParentPomName = form.BPomFile.data
    # Save values to session data
    session['ParentPomPath'] = D.ParentPomPath
    session['ParentPomName'] = D.ParentPomName
    # Advance to next build rule
    R.NextRule()

def render_select_pom(form, T, D):
    '''
        Handle GET event on build/build.html
    '''
    set_pom(D)
    return render_template('select.html', form=form, T=T, D=D)

# Execute Build Steps
# ==========================================

def submit_build(form, R, T, D):
    '''
        Handle a submit (POST) event on build/build.html.
        This is the controller for stepping through a Rule set:
        Handle each of the build steps:
    self.RuleSet = {'build_app':{0:T.Texts['pomGet'],
                                 1:T.Texts['pomRead'],
                                 2:T.Texts['pomEval'],
                                 3:T.Texts['buildDirectories'],
                                 4:T.Texts['buildControls'],
                                 5:T.Texts['checkPackages'],
                                 6:T.Texts['checkServices'],
                                 7:T.Texts['buildDone']}}
    '''
    if R.RuleIdx == 1:
        # Store the Pom file data in structured memory
        D.StatusMsg.append(T.Texts['pomGot'])
        D.LoadPomFile()
    elif R.RuleIdx == 2:
        # Evaluate and modify the stored data as needed
        D.StatusMsg.append(T.Texts['pomLoaded'])
        D.EvalPomFile(T)
        # Jump to end if failure code returned
        if D.StatusCode == 99:
            R.RuleIdx = R.LastRuleIdx
    elif R.RuleIdx == 3:
        # Construct the application directories
        D.StatusMsg.append(T.Texts['pomEvaled'])
        D.BuildDirs(T)
    elif R.RuleIdx == 4:
        # Construct and post control files
        D.StatusMsg.append(T.Texts['builtDirectories'])
        D.BuildIndexFiles(T)
        # Jump to end if failure code returned
        if D.StatusCode == 99:
            R.RuleIdx = R.LastRuleIdx
    elif R.RuleIdx == 5:
        # Check for presence of packages on system
        D.StatusMsg.append(T.Texts['builtControls'])
        D.CheckPackages(T)
        if D.StatusCode == 99:
            R.RuleIdx = R.LastRuleIdx
    elif R.RuleIdx == 6:
        # Check for services running on the system
        D.StatusMsg.append(T.Texts['checkedPackages'])
        D.CheckServices(T)
        if D.StatusCode == 99:
            R.RuleIdx = R.LastRuleIdx
    elif R.RuleIdx == 7:
        # Show completion notice
        if R.ProcessLastStep and not R.ProcessCompleted:
            D.StatusMsg.append(T.Texts['checkedServices'])
            if D.StatusCode == 0:
                D.StatusCode = 1
                D.StatusMsg.append(T.Texts['buildDoneOK'])
            elif D.StatusCode == 99:
                D.StatusMsg.append(T.Texts['buildDoneError'])
            else:
                D.StatusMsg.append(T.Texts['buildDoneWarn'])
    # Advance to next build rule
    R.NextRule()

def render_build(form, R, T, D):
    '''
        Handle GET event on build/build.html
    '''
    return render_template('build.html', form=form, R=R, T=T, D=D)

# Handle Report Requests
# ==========================================
def submit_report(form, T, D):
    '''
        Handle a submit event (POST) on report/report.html
    '''
    #debug
    print 'TAG: Present and handle report requests'

def render_report(form, T, D):
    '''
        Handle a GET event on report/report.html
    '''
    #debug
    print 'TAG: Present and handle report requests'
    return render_template('report.html', form=form, T=T, D=D)

if __name__ == '__main__':
  pass
