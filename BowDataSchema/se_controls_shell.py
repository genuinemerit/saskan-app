#!/usr/bin/python3.9
"""
:module:    se_controls_shell.py

:author:    GM (genuinemerit @ pm.me)

Service Activator / Deactivator class for Data Schema services.
"""
# import subprocess as shl
import os
import time

# from pprint import pprint as pp

from BowQuiver.saskan_utils import Utils            # type: ignore
from BowQuiver.saskan_texts import SaskanTexts      # type: ignore

UT = Utils()
TX = SaskanTexts()


class ControlsShell(object):
    """Run Controller-related commands."""

    def __init__(self):
        """Initialize the object."""
        self.PYPATH = \
            "/home/dave/Dropbox/Apps/BoW/bow-data-schema/BowDataSchema/"

    def start_services(self,
                       p_service_nm: str) -> tuple:
        """Start a service.
        Starts up server, requestor and responder for a service.
        Eventually requestor would be for testing only.

        Using nohup prevents the background process from dying if
        the python context closes. However, it writes log data to a
        local file called "nohup.out". This file should be deleted or
        scraped.

        As in an earlier prototype, we will want to have an installer
        that moves all the python code to the App directory, in which
        case it might be OK to leave the nohup.out file in same dir
        with the python files. Note that nothing is being written to
        the /tmp/*.log files. May want to change that to /dev/null.

        The bottom line is that anything of any interest should be
        directed to the wiretap module. Speaking of which, I think
        the saskan_logger module can work as a proto-wiretap module.
        Will want to have it write to Redis Monitor and Log instead of
        to a flat log file. And should use redis_io to do that, which
        in turn implies that the record types, structs should be defined
        for its use.

        Args:
            p_service_nm (str) name of service to start
        Returns:
            tuple: (is_started: bool, msg: str)
        """
        server_nm = p_service_nm + "_server.py"
        is_running, msg = self.check_running_services(server_nm)
        if is_running:
            return(True, f"{server_nm} already running.")
        else:
            svc_msg = ""
            for pgm in ("server", "response", "request"):
                cmd = "nohup python3.9 -u "
                cmd += f"{self.PYPATH}{p_service_nm}_{pgm}.py &> "
                cmd += f"/tmp/saskan_svc_{p_service_nm}_{pgm}.log &"
                try:
                    os.system(cmd)
                    svc_msg += f"\n{p_service_nm}_{pgm}.py started."
                except Exception as e:
                    svc_msg += f"\n{p_service_nm}_{pgm}.py failed to start."
                    svc_msg += f"\n{e}"
                    self.stop_services(p_service_nm)
                    return (False, svc_msg)
            return (True, svc_msg)

    def stop_services(self,
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
        return (is_running, show_msg)

    def check_running_services(self,
                               p_service_nm: str) -> tuple:
        """Check if a service is running.

        Treid modifying to check for service name that includes
        an underbar, but didn't seem to work as desired.
        Perhaps need to explicitly exclude redis-server and
        redis-sentinel.

        Args:
            p_service_nm (str) name of service to check
        Returns:
            tuple: (is_running: bool, msg: str)
        """
        cmd = f"ps -ef | grep -v grep | grep {p_service_nm} "
        cmd += "| grep -wv redis-server | grep -wv redis-sentinel"
        _, result = UT.run_cmd(cmd)
        is_running = True if p_service_nm in result else False
        show_msg = f"\nLooked for services like *..{p_service_nm[-32:]}*"
        result = result.strip("\n").strip()
        if result in (None, ""):
            result = "No services found."
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
            show_msg += f"\n{p_service_nm} is not running."
        return (is_stopped, show_msg)
