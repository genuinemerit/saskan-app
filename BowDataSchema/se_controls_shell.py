#!/usr/bin/python3.9
"""
:module:    se_controls_shell.py

:author:    GM (genuinemerit @ pm.me)

Service Activator / Deactivator class for Data Schema services.

@DEV:
- Avoid having to call a bash shell script
- Submit OS commands directly from this program
- Check out recipe in the Python Cookbook for launching a Linux daemon
  process from a python script.
"""
import time
from BowQuiver.saskan_utils import Utils            # type: ignore
from BowQuiver.saskan_texts import SaskanTexts      # type: ignore
UT = Utils()
TX = SaskanTexts()


class ControlsShell(object):
    """Run Controller-related commands."""

    def check_running_services(self,
                               p_service_nm: str) -> tuple:
        """Check if a service is running.
        Args:
            p_service_nm (str) name of service to check
        Returns:
            tuple: (is_running: bool, msg: str)
        """
        cmd = f"ps -ef | grep -v grep | grep {p_service_nm}"
        _, result = UT.run_cmd(cmd)
        is_running = True if p_service_nm in result else False
        show_msg = f"\nLooked for services like *..{p_service_nm[-32:]}*"
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
            show_msg += f"\n{p_service_nm} stopped."
        return (is_stopped, show_msg)
