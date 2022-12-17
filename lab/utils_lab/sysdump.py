import site
import sys

def showsys():
	'''Display a variety of sys and site settings
	'''
	print("\nSITE settings\n==================")
	site.addsitedir('/home/david/Projects/BlackTuna/python')
	print("site.PREFIXES\t\t", repr(site.PREFIXES), "\t\t\t\t\t\tPrefixes for site-package dirs")
	print("site.USER_BASE\t\t", repr(site.USER_BASE), "\t\t\t\t\t\tDefault base dir for user site-packages")
	print("site.USER_SITE\t\t", repr(site.USER_SITE), "\t\tDefault location for local modules")
	print("site.ENABLE_USER_SITE\t", repr(site.ENABLE_USER_SITE), "\t\t\t\t\t\t\t\tWhether or not USER_SITE is being used")

	print("\nSYS settings\n==================")
	print("sys.abiflags\t\t", repr(sys.abiflags), "\t\t\tThe ABI flags for this POSIX system.")
	print("sys.argv\t\t", repr(sys.argv), "\tThe list of command line arguments passed to python script.")
	print("sys.base_exec_prefix\t", repr(sys.base_exec_prefix), "\t\tWhere platform-dependent Python files are originally installed.")
	print("sys.exec_prefix\t\t", repr(sys.exec_prefix), "\t\tWhere platform-dependent Python files are installed, reflecting any virtualization.")
	print("sys.prefix\t\t", repr(sys.prefix), "\t\tWhere platform-independent Python files are installed.")
	print("sys.byteorder\t\t", repr(sys.byteorder), "\t\tBig-endian (most significant byte first) vs. little-endian (least sig first)")
	print("sys.platform\t\t", repr(sys.platform), "\t\tA platform identifier")
	print("sys.version\t\t", repr(sys.version), "\t\tVersion info for the python interpreter")
	print("\nsys.builtin_module_names\t\t\tNames of all pre-compiled modules:\n", repr(sys.builtin_module_names))
	print("\nsys.modules\t\t\tNames of all loaded modules:\n", repr(sys.modules))
	print("\nsys.path\t\t\t\t\tSpecifies the search path for all modules, first local path, then PYTHONPATH, then paths added using site.addsitedir:\n", repr(sys.path))
	print("\nsys.meta_path\t\t\tNames of finder objects:\n", repr(sys.meta_path))
	print("\nsys.copyright\t\t", repr(sys.copyright))
	print("\nsys.getdefaultencoding\t\t", repr(sys.getdefaultencoding))
	print("sys.getfilesystemencoding\t", repr(sys.getfilesystemencoding))
	print("sys.implementation\t\t", repr(sys.implementation))
	
	
if __name__ == '__main__':
	site.main()
	showsys()
