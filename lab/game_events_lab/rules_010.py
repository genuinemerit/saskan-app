'''
    This module defines Class AppData for handling in-memory data
    structures for the app, along with most of the logic for executing
    the Rules.

    Two things here:
    * A module that handles all error messages (and similar.. in fact monitors for them)
      would be A Good Thing
    * This is basically a continuation of the "rules.py" module. The use case was for a build
      machine, which I would probably no longer handle this way. But it could be an interesting
      approach to game play.
'''
# python packages
import os
import sys
import xml.etree.ElementTree as ET
# Local packages
sys.path.append('app')
import main
from main import utils
# ==============================================
class AppData:
  '''
    Structure and methods for storing data about the Build in memory.
     Methods in this class implement the rules defined in rules.py.
     They store information within this class and also affect the
     structure of target directories and files.
  '''
  def __init__(self):
    '''
        Instantiate AppData object.
    '''
    # XML Containers
    self.PomTree = None
    self.PomRoot = None
    self.RootURL = ''
    self.RootTag = ''
    # Pom File location values.
    self.ParentPomPath = ''
    self.ParentPomName = ''
    self.PomFilePath = ''
    # Tags
    self.PomKeys = []
    self.PomValues = {}
    # Targets
    self.SystemPath = ''
    self.DirStruct = {}
    self.DirList = []
    self.DirListLen = 0
    self.FileList = []
    self.FileListLen = 0
    self.PkgList = []
    self.PkgListLen = 0
    self.SvcList = []
    self.SvcListLen = 0
    # Status
    self.StatusCode = 0
    self.StatusMsg = []

  def ResetStructs(self):
    '''
        (Re-)Initialize the values in AppData object.
    '''
    self.PomTree = None
    self.PomRoot = None
    self.RootURL = ''
    self.RootTag = ''
    self.PomRecs = []
    self.ParentPomPath = ''
    self.ParentPomName = ''
    self.PomFilePath = ''
    self.PomKeys = ['groupId','artifactId','packaging','version','name',
                    'description','url','inceptionYear','organization',
                    'licenses','developers','scm','issueManagement',
                    'build','components','prerequisites','parent','modules',
                    'dependencies']
    self.PomValues = {}
    self.SystemPath = ''
    self.DirStruct = {}
    self.DirList = []
    self.DirListLen = 0
    self.FileList = []
    self.FileListLen = 0
    self.PkgList = []
    self.PkgListLen = 0
    self.SvcList = []
    self.SvcListLen = 0
    self.StatusCode = 0
    self.StatusMsg =  ['started']

  # Error handlers for this Class
  # =================================
  def SetBadValueErr(self, tag, T):
      '''
        Bad Value Error
      '''
      self.StatusMsg.append('[' + T.Texts['err'] + '] ' + T.Texts['badValue'] + ': ' + tag)
      self.StatusCode = 99

  def SetMissingEnvironErr(self, tag, T):
      '''
        Missing Environmental Variable Error
      '''
      self.StatusMsg.append('[' + T.Texts['err'] + '] ' + T.Texts['noEnviron'] + ': ' + tag)
      self.StatusCode = 99

  def SetMissingPackageMsg(self, tag, T, mlvl):
      '''
        Missing Software Package Message
      '''
      if mlvl == 'W':
        self.StatusMsg.append('[' + T.Texts['wrn'] + '] ' + T.Texts['noPackage'] + ': ' + tag)
        if self.StatusCode < 89:
			self.StatusCode = 89
      elif mlvl == 'E':
        self.StatusMsg.append('[' + T.Texts['err'] + '] ' + T.Texts['noPackage'] + ': ' + tag)
        self.StatusCode = 99

  def SetMissingServiceMsg(self, tag, T, mlvl):
      '''
        Missing Software Service Message
      '''
      if mlvl == 'W':
        self.StatusMsg.append('[' + T.Texts['wrn'] + '] ' + T.Texts['noService'] + ': ' + tag)
        if self.StatusCode < 89:
			self.StatusCode = 89
      elif mlvl == 'E':
        self.StatusMsg.append('[' + T.Texts['err'] + '] ' + T.Texts['noService'] + ': ' + tag)
        self.StatusCode = 99

  def SetMissingValueErr(self, tag, T):
      '''
        Missing Value Error
      '''
      self.StatusMsg.append('[' + T.Texts['err'] + '] ' + T.Texts['noValue'] + ': ' + tag)
      self.StatusCode = 99

  def SetUnknownDirErr(self, tag, T):
      '''
        Bad or Unknown Directory Error
      '''
      self.StatusMsg.append('[' + T.Texts['err'] + '] ' + T.Texts['badDir'] + ': ' + tag)
      self.StatusCode = 99

  # The following methods are associated with the first build rule.
  # ===================================================================
  def LoadPomFile(self):
    '''
        Controlling method (Step 1) for the first Rule.
        Run the first rule: Read in the POM XML file
    '''
    self.PomFilePath = os.path.join(self.ParentPomPath, self.ParentPomName)
    if self.PomFilePath != '' and utils.verify_path(self.PomFilePath):
        # Create an ElementTree object
        self.PomTree = ET.parse(self.PomFilePath)
        # Create an Element object
        self.PomRoot = self.PomTree.getroot()
        # Split off the Namespace URL associated with the root tag
        rootvalues = self.PomRoot.tag.split('}', 1)
        # Save root values
        self.RootURL = rootvalues[0] + '}'
        self.RootTag = rootvalues[1]
        # Parse and save the elements
        for tag in self.PomKeys:
            self.SavePomData(tag)
    else:
        print 'No POM file defined'

  def SavePomData(self, tag):
    '''
        Step 2 for the first Rule.
        Process and save data for all the child elements in the POM XML.
    '''
    # Start a dictionary item for the curent element
    self.PomValues[tag] = {}
    # Get all elements under root which match this tag
    searchtag = self.RootURL + tag
    elems = self.PomRoot.findall(searchtag)
    etext = None
    for elem in elems:
        # Determine if it has any children or just text
        if elem.text:
            etext = elem.text.strip()
        if etext or elem.text == None:
            # Store text value for simple elements
            self.PomValues[tag]['value'] = etext
        else:
            self.SaveTheChildren(tag, elem)

  def SaveTheChildren(self, tag, elem):
    '''
        Step 3 for the first Rule.
        Break down the handling of simple and complex child elements.
    '''
    # Handle Pom attributes of simple children
    if tag == 'organization':
        ctags = ['name', 'url']
        self.SaveChildValues(tag, ctags, elem)
    elif tag == 'scm':
        ctags = ['connection', 'developerConnection', 'tag', 'url']
        self.SaveChildValues(tag, ctags, elem)
    elif tag == 'issueManagement':
        ctags = ['system', 'url']
        self.SaveChildValues(tag, ctags, elem)
    # Handle Pom attributes of complex children
    elif tag == 'licenses':
        tag2 = 'license'
        ctags = ['name', 'url', 'distribution', 'comments']
        self.SaveTheGrandChildren(tag, tag2, ctags, elem)
    elif tag == 'developers':
        tag2 = 'developer'
        ctags = ['id', 'name', 'email', 'url', 'organization', 'organizationUrl',
                 'roles', 'timezone']
        self.SaveTheGrandChildren(tag, tag2, ctags, elem)
    elif tag == 'dependencies':
        tag2 = 'dependency'
        ctags = ['groupId', 'artifactId', 'version', 'type', 'classifier',
                 'comments','scope','systemPath','parentdependency',
                 'exclusions','optional']
        self.SaveTheGrandChildren(tag, tag2, ctags, elem)

  def SaveChildValues(self, tag, ctags, elem):
    '''
        Step 4 for the first Rule.
        Handle saving values for the simple child elements.
    '''
    t = 0
    for ctag in ctags:
        self.PomValues[tag][ctag] = {'value':elem[t].text}
        t += 1

  def SaveTheGrandChildren(self, tag, tag2, ctags, elem):
      '''
        Step 5 for the first Rule.
        Store tags and values of the complex children
      '''
      self.PomValues[tag][tag2] = {}
      searchtag = self.RootURL + tag2
      elems2 = elem.findall(searchtag)
      etext = None
      eIdx = -1
      for elem2 in elems2:
          eIdx += 1
          self.PomValues[tag][tag2][eIdx] = {}
          t = 0
          for ctag in ctags:
              self.PomValues[tag][tag2][eIdx][ctag] = {'value':elem2[t].text}
              t += 1

  # The following methods are associated with second build rule.
  # =====================================================================
  def EvalPomFile(self, T):
      '''
      Control method for Rule #2.
      Step #1: Convert standard substitutions to corresponding project values.
      Edit for bad or missing values in the dependency elements.
      '''
      # Control the Pom evaluation logic
      # Get the project version and groupId values
      projver = self.PomValues['version']['value']
      projgrp = self.PomValues['groupId']['value']
      # Make standard substitutions in dependencies
      deps = self.PomValues['dependencies']['dependency']
      # Do edits for project attributes and in root dependency
      self.EditPomValues(deps[0], T)
      if self.StatusCode == 0:
          # Do edits for all dependencies
          for k, dep in deps.items():
              # convert ${project.version}
              cvtval = dep['version']['value'].replace("${project.version}", projver)
              self.PomValues['dependencies']['dependency'][k]['version']['value'] = cvtval
              # convert ${project.groupId}
              cvtval = dep['groupId']['value'].replace("${project.groupId}", projgrp)
              self.PomValues['dependencies']['dependency'][k]['groupId']['value'] = cvtval
              # edit for non-empty artifactId (= directory name)
              if len(dep['artifactId']['value']) < 1:
                  self.SetMissingValueErr('dependency # ' + k + ' [artifactId]', T)
              # edit for non-empty parentdependency if type value is dir
              if dep['type']['value'] == 'dir':
                  if dep['parentdependency']['value'] is None or len(dep['parentdependency']['value']) < 1:
                    self.SetMissingValueErr('dependency # ' + k + ' [parentdependency]', T)

  def EditPomValues(self, deproot, T):
      '''
      Step #2 of the Second Rule.
      Edit for bad or missing values in the project attributes and the root
      dependency element.  Normalize the system path.
      '''
      tags = ['artifactId', 'name', 'version']
      for tag in tags:
          if self.PomValues[tag]['value'] == None or self.PomValues[tag]['value'] == '':
             self.SetMissingValueErr('project attribute [' + tag + ']', T)
      # Edit for root dependency artifact type
      if deproot['type']['value'] != 'path':
         self.SetBadValueErr('root dependency [type]', T)
      # Edit for missing system path in root dependency
      if len(deproot['systemPath']['value']) < 1:
         self.SetMissingValueErr('root dependency [systemPath]', T)
      # Verify and normalize system path
      self.SystemPath = utils.verify_path(self.PomValues['dependencies']['dependency'][0]['systemPath']['value'])
      if self.SystemPath:
         self.PomValues['dependencies']['dependency'][0]['systemPath']['value'] = self.SystemPath
      else:
         self.SetBadValueErr('root dependency [systemPath]', T)

  # The following method is associated with third build rule.
  # =====================================================================
  def BuildDirs(self, T):
      '''
        Control method and single step for the Third Build Rule.
        Design the target directory architecture.
        Create target directories as needed based on the POM dependencies.
        Document the target directory structures.
      '''
      deps = self.PomValues['dependencies']['dependency']
      artid = ''
      prv_artid = []
      parentdep = ''
      self.DirList = []
      self.DirListLen = 0
      # Spin thru the dependencies for deps where type is path or dir
      for k, dep in deps.items():
          if dep['type']['value'] in ['path', 'dir']:
              # Get the directory name and parent directory name
              artid = dep['artifactId']['value']
              parentdep = dep['parentdependency']['value']
              # See if the parent name shows up anywhere in the previously-defined dirs
              # If so, then append to it and store the new dir path
              for pdir in prv_artid:
                  if parentdep in pdir:
                     artid = pdir + '/' + artid
                     break
              # Assemble a full, real path to the new dir
              thisdir = os.path.join(self.SystemPath, artid)
              # See if the new dir already exists
              isDir = utils.verify_path(thisdir)
              if isDir:
                  # Already exists, so just document it
                  self.DirList.append(isDir)
              else:
                  # Create the new directory and document it
                  os.mkdir(thisdir)
                  self.DirList.append(thisdir)
              prv_artid.append(artid)
      self.DirListLen = len(self.DirList)

  # The following methods are associated with Fourth build rule.
  # =====================================================================

  def BuildIndexFiles(self, T):
      '''
        Control method and Step #1 of the Fourth Rule.  Create standard files.

        For directories of type 'path', create NOTIFY.md using project-level dep info
        For directories of classifier 'web', create index.html
        For directories of classifier 'python', create __init__.py and index.html
      '''
      # Spin thru the deps
      self.FileList = []
      self.FileListLen = 0
      deps = self.PomValues['dependencies']['dependency']
      # Spin thru the dependencies for deps where type is path or dir
      for k, dep in deps.items():
          if dep['type']['value'] in ['path', 'dir']:
              # Get the corresponding dir
              thisdir = self.AlignDirAndDep(dep)
              # Error out if no dir aligned to the dep
              if thisdir == '':
                  self.SetUnknownDirErr('dependency artifactId [' + artid + ']', T)
                  break
              # Create docs in dir for this dep
              dirtype = dep['type']['value']
              dircls = dep['classifier']['value']
              # Which doc
              if dirtype == 'path':
                  self.CreateRootDocs(thisdir, T)
              if dircls == 'web':
                  self.CreateIndexDoc(thisdir, dep, T)
              elif dircls == 'python':
                  self.CreateInitPyDoc(thisdir, dep, T)
      self.FileListLen = len(self.FileList)

  def AlignDirAndDep(self, dep):
      '''
        Step #2 of the Fourth Rule.
        Make sure dependency element is aligned to the right directory
      '''
      thisdir = ''
      # Spin thru the list of directories
      for pdir in self.DirList:
          # Get the dependency's artifactId and parentdependency values
          artid = dep['artifactId']['value']
          parentdep = dep['parentdependency']['value']
          # Break out the directory into parts
          pathparts = pdir.split('/')
          # Get the last and second-to-last parts
          z = len(pathparts) - 1
          zpart = pathparts[z]
          ypart = pathparts[z-1]
          if zpart == artid:
              # dependency artifactId matches the directory
              if parentdep == None or parentdep == ypart:
                  # dependency parentdependency matches the parent directory
                  thisdir = pdir
                  break
      return thisdir

  def CreateRootDocs(self, thisdir, T):
      '''
        Step #3 of the Fourth Rule.
        Create documents in the root directory.
      '''
      # Check for NOTIFY.md
      thisfile = os.path.join(thisdir, 'NOTIFY.md')
      filepath = utils.verify_path(thisfile)
      if not filepath:
          self.CreateNotifyDoc(thisfile, T)
      # Check for LICENSE.md
      thisfile = os.path.join(thisdir, 'LICENSE.md')
      filepath = utils.verify_path(thisfile)
      if not filepath:
          self.createLicenseDoc(thisfile, T)
      # Check for README.md
      thisfile = os.path.join(thisdir, 'README.md')
      filepath = utils.verify_path(thisfile)
      if not filepath:
          self.createReadMeDoc(thisfile, T)

  def CreateNotifyDoc(self, thisfile, T):
      '''
        Step #4 of the Fourth Rule.
        Create the NOTIFY.md file.
      '''
      # Create file
      self.FileList.append(thisfile)
      f = open(thisfile, 'wb')
      # Application Identification
      f.write(utils.fmt_title(T.Texts['aboutApp']))
      f.write(utils.fmt_nmval(T.Texts['projAppName'], self.PomValues['name']['value']))
      f.write(utils.fmt_nmval(T.Texts['projAppVersion'], self.PomValues['version']['value']))
      f.write(utils.fmt_nmval(T.Texts['projAppDesc'], self.PomValues['description']['value']))
      f.write(utils.fmt_nmurl(T.Texts['projAppAboutUrl'], self.PomValues['url']['value']))
      # Organization Info
      f.write('\n')
      f.write(utils.fmt_nmval(T.Texts['projOrg'], self.PomValues['organization']['name']['value']))
      f.write(utils.fmt_nmurl(T.Texts['projOrgAboutUrl'], self.PomValues['organization']['url']['value']))
      f.write(utils.fmt_nmval(T.Texts['projYear'], self.PomValues['inceptionYear']['value']))
      # License Info
      f.write(utils.fmt_title(T.Texts['licenses']))
      for k, licdep in self.PomValues['licenses']['license'].items():
          f.write(utils.fmt_nmval(T.Texts['projLicenseName'], licdep['name']['value']))
          f.write(utils.fmt_nmurl(T.Texts['projLicenseAboutUrl'], licdep['url']['value']))
          f.write(utils.fmt_nmval(T.Texts['projLicenseComment'], licdep['comments']['value']))
          f.write(utils.fmt_nmval(T.Texts['projLicenseDist'], licdep['distribution']['value']))
          f.write('\n')
      # SCM and Distribution Info
      f.write(utils.fmt_title(T.Texts['codeDist']))
      f.write(utils.fmt_nmurl(T.Texts['projScmUrl'], self.PomValues['scm']['url']['value']))
      f.write(utils.fmt_nmval(T.Texts['projScmConnect'], self.PomValues['scm']['connection']['value']))
      f.write(utils.fmt_nmval(T.Texts['projScmDevConnect'], self.PomValues['scm']['developerConnection']['value']))
      f.write(utils.fmt_nmval(T.Texts['projScmTag'], self.PomValues['scm']['tag']['value']))
      # Project Info
      f.write(utils.fmt_title(T.Texts['devSupport']))
      f.write(utils.fmt_nmval(T.Texts['projRootDir'], self.PomValues['artifactId']['value']))
      f.write(utils.fmt_nmval(T.Texts['projIssueSys'], self.PomValues['issueManagement']['system']['value']))
      f.write(utils.fmt_nmurl(T.Texts['projIssueSysAboutUrl'], self.PomValues['issueManagement']['url']['value']))
      # Developer Info
      f.write(utils.fmt_title(T.Texts['devs']))
      for k, dev in self.PomValues['developers']['developer'].items():
          f.write(utils.fmt_nmval(T.Texts['projDevName'], dev['name']['value']))
          f.write(utils.fmt_nmval(T.Texts['projDevId'], dev['id']['value']))
          f.write(utils.fmt_nmval(T.Texts['projDevEmail'], dev['email']['value']))
          f.write(utils.fmt_nmurl(T.Texts['projDevUrl'], dev['url']['value']))
          f.write(utils.fmt_nmval(T.Texts['projDevRoles'], dev['roles']['value']))
          f.write(utils.fmt_nmval(T.Texts['projDevZone'], dev['timezone']['value']))
          f.write(utils.fmt_nmval(T.Texts['projDevOrg'], dev['organization']['value']))
          f.write(utils.fmt_nmurl(T.Texts['projDevOrgUrl'], dev['organizationUrl']['value']))
          f.write('\n')
      # Close file
      f.close

  def createLicenseDoc(self, thisfile, T):
      '''
        Step #5 of the Fourth Rule.
        Create the LICENSE.md file.
      '''
      # Create file
      self.FileList.append(thisfile)
      f = open(thisfile, 'wb')
      f.write(utils.fmt_instruct(T.Texts['replaceLicense']))
      # Close file
      f.close

  def createReadMeDoc(self, thisfile, T):
      '''
        Step #6 of the Fourth Rule.
        Create the README.md file.
      '''
      # Create file
      self.FileList.append(thisfile)
      f = open(thisfile, 'wb')
      f.write(utils.fmt_instruct(T.Texts['replaceReadme']))
      # Close file
      f.close

  def CreateIndexDoc(self, thisdir, dep, T):
      '''
        Step #7 of the Fourth Rule.
        Create index.html files.
      '''
      # Check for index.html
      thisfile = os.path.join(thisdir, 'index.html')
      filepath = utils.verify_path(thisfile)
      if not filepath:
          # Create file
          self.FileList.append(thisfile)
          f = open(thisfile, 'wb')
          f.write(utils.fmt_html_start(T.Texts['forbid']))
          msg = utils.fmt_html_nmval(T.Texts['depdir'], dep['artifactId']['value'])
          if dep['comments']['value'] == None:
              cmt = 'None'
          else:
              cmt = dep['comments']['value']
          msg += utils.fmt_html_nmval(T.Texts['depNotes'], cmt)
          f.write(utils.fmt_html_end(msg))
          # Close file
          f.close

  def CreateInitPyDoc(self, thisdir, dep, T):
      '''
        Step #8 of the Fourth Rule.
        Create __init__.py files.
      '''
      # Check for __init__.py
      thisfile = os.path.join(thisdir, '__init__.py')
      filepath = utils.verify_path(thisfile)
      if not filepath:
          # Create file
          self.FileList.append(thisfile)
          f = open(thisfile, 'wb')
          f.write(T.Texts['pyBang'] + '\n')
          f.write("'''\n")
          f.write(utils.fmt_nmval(T.Texts['depdir'], dep['artifactId']['value']))
          if dep['comments']['value'] == None:
              cmt = 'None'
          else:
              cmt = dep['comments']['value']
          f.write(utils.fmt_nmval(T.Texts['depNotes'], cmt))
          f.write("'''\n")
          # Close file
          f.close

  # The following methods are associated with Fifth build rule.
  # =====================================================================

  def CheckPackages(self, T):
      '''
        Control module and Step #1 of the Fifth Rule.
        Check to see if required packages are present on the system.
      '''
      deps = self.PomValues['dependencies']['dependency']
      # Spin thru the dependencies for deps where type is pkg

      self.PkgList = []
      self.PkgListLen = 0
      for k, dep in deps.items():
          if dep['type']['value'] == 'pkg':
              pkgnm = dep['artifactId']['value']
              pkgis = utils.whereis_pkg(pkgnm)
              if not pkgis:
                  if dep['optional']['value'] == 'false':
                    self.SetMissingPackageMsg(pkgnm, T, 'E')
                  else:
                    self.SetMissingPackageMsg(pkgnm, T, 'W')
              else:
                  self.PkgList.append(pkgis)
      self.PkgListLen = len(self.PkgList)

  # The following methods are associated with Sixth build rule.
  # =====================================================================

  def CheckServices(self, T):
      '''
        Control module and Step #1 of the Sixth Rule.
        Check to see if required services are running on the system.
      '''
      deps = self.PomValues['dependencies']['dependency']
      # Spin thru the dependencies for deps where type is svc

      self.SvcList = []
      self.SvcListLen = 0
      for k, dep in deps.items():
          if dep['type']['value'] == 'svc':
              svcnm = dep['artifactId']['value']
              svcis = utils.grep_process(svcnm)
              if not svcis:
                  if dep['optional']['value'] == 'false':
                    self.SetMissingServiceMsg(svcnm, T, 'E')
                  else:
                    self.SetMissingServiceMsg(svcnm, T, 'W')
              else:
                  self.SvcList.append(svcis)
      self.SvcListLen = len(self.SvcList)
