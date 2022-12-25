#!python
"""Saskan Apps file configuration / install / set-up.
:module:    saskan_install.py
:class:     SaskanInstall/0
:author:    GM <genuinemerit @ pm.me>

Requires sudo privs to execute properly.
Writes bash files to /usr/local/bin
Launch it by running sudo ./saskan_install from the git project directory,
e.g. (saskan) ~/../Saskantinon/saskan_install
"""
import json
import os

from os import path
from pathlib import Path
from pprint import pprint as pp     # noqa: F401
# from time import sleep

from io_file import FileIO          # type: ignore
from io_shell import ShellIO        # type: ignore

FI = FileIO()
SI = ShellIO()


class SaskanInstall(object):
    """Configure and install set-up for Saskan apps.

    Bootstrap dirs configuration metadata from project directory.
    Use current working directory (git project) to derive home directory.
    """
    def __init__(self):
        """Initialize directories and files.
        """
        self.verify_bash_bin_dir()
        self.APP = path.join("/home", Path.cwd().parts[2], FI.D['APP'])
        self.create_app_space()
        self.install_app_files()
        self.copy_python_scripts()
        self.copy_bash_files()
        self.set_topics(self.set_channels())
        FI.pickle_saskan(self.APP)
        self.start_servers()

    # Helpers
    # ==============================================================

    def verify_bash_bin_dir(self):
        """Verify standard bash directory exists.
        - /usr/local/bin
        """
        ok, err, _ = FI.get_dir(FI.D["BIN"])
        if not ok:
            raise Exception(f"{FI.T['err_file']} {FI.D['BIN']} {err}")

    # Directory, file, record set-up
    # ==============================================================

    def create_app_space(self):
        """If app dir already exists, delete everything.
        Create sakan app directory.
        Create sakan app sub-dirs.
        Create namesapce sub-dirs.
        """
        # App dir
        ok, err, _ = FI.get_dir(self.APP)
        if ok:
            # Delete everything in app dir
            app_files = self.APP + "/*"
            ok, result = SI.run_cmd([f"sudo rm -rf {app_files}"])
            if not ok:
                raise Exception(f"{FI.T['err_process']} {result}")
            ok, result = SI.run_cmd([f"sudo rmdir {self.APP}"])
            if not ok:
                raise Exception(f"{FI.T['err_process']} {result}")
        ok, err = FI.make_dir(self.APP)
        if ok:
            ok, err = FI.make_executable(self.APP)
        if not ok:
            raise Exception(f"{FI.T['err_process']} {err}")
        # App sub-dirs
        for _, sub_dir in FI.D['ADIRS'].items():
            sdir = path.join(self.APP, sub_dir)
            ok, err = FI.make_dir(sdir)
            if ok:
                ok, err = FI.make_executable(sdir)
            if not ok:
                raise Exception(f"{FI.T['err_file']} {sdir} {err}")
        # Namespace sub-dirs
        for _,  sub_dir in FI.D['NSDIRS'].items():
            sdir = path.join(self.APP, FI.D['ADIRS']['SAV'], sub_dir)
            ok, err = FI.make_dir(sdir)
            if ok:
                ok, err = FI.make_executable(sdir)
                if ok:
                    ok, err = FI.make_writable(sdir)
            if not ok:
                raise Exception(f"{FI.T['err_file']} {sdir} {err}")

    def install_app_files(self):
        """Copy config, image and schema/ontology files"""
        for sdir in (FI.D['ADIRS']['CFG'],
                     FI.D['ADIRS']['IMG'],
                     FI.D['ADIRS']['ONT']):
            src_dir = path.join(Path.cwd(), sdir)
            ok, err, files = FI.get_dir(src_dir)
            if not ok:
                raise Exception(f"{FI.T['err_file']} {src_dir} {err}")
            FI.copy_files(path.join(self.APP, sdir), files)

    def copy_python_scripts(self):
        """Copy - python (*.py) files --> /python
        Excluding installer scripts.
        """
        ok, err, files = FI.get_dir(Path.cwd())
        if not ok:
            raise Exception(f"{FI.T['err_file']} {Path.cwd()} {err}")
        py_files = [f for f in files if str(f).endswith(".py") and
                    "_install" not in str(f)]
        tgt_dir = path.join(self.APP, FI.D['ADIRS']['PY'])
        for f in py_files:
            if Path(f).is_file():
                tgt_file = path.join(tgt_dir, str(f).split("/")[-1])
                ok, err = FI.copy_file(str(f), tgt_file)
                if not ok:
                    raise Exception(
                        f"{FI.T['err_file']} {tgt_file} {err}")

    def copy_bash_files(self):
        """Copy /bash to /usr/local/bin

        Set up the command-line exectuables for saskan.
        Modify before copying to correctly locate the
        python files in the saskan app directory.
        """
        src_dir = path.join(Path.cwd(), "bash")
        py_dir = path.join(self.APP, FI.D['ADIRS']['PY'])
        ok, err, files = FI.get_dir(src_dir)
        if not ok:
            raise Exception(f"{FI.T['err_file']} {src_dir} {err}")
        for bf in files:
            bf_name = str(bf).split("/")[-1]
            tgt_file = path.join(FI.D['BIN'], bf_name)
            ok, err, bf_code = FI.get_file(str(bf))
            if not ok:
                raise Exception(f"{FI.T['err_file']} {bf} {err}")
            bf_code = bf_code.replace("~APP_DIR~", py_dir)
            ok, err = FI.write_file(tgt_file, bf_code)
            if not ok:
                raise Exception(f"{FI.T['err_file']} {tgt_file} {err}")
            ok, err = FI.make_executable(tgt_file)
            if not ok:
                raise Exception(f"{FI.T['err_file']} {tgt_file} {err}")

    def set_channels(self):
        """Set channel info based on schema metadata"""

        def get_host_IPs():
            """Convert host name(s) to IP address(es)"""
            for host in FI.S['channels']['resources']['hosts']:
                ok, result = SI.run_cmd([f"grep {host} /etc/hosts"])
                if ok:
                    hosts = [h for h in result.split() if h != host] + [host]
            return hosts

        def init_channels():
            """Initialize channel dictionary"""
            total_port_cnt = 0
            channels = dict()
            for ch_nm, port_meta in FI.S['channels']['named'].items():
                channels[ch_nm] = {"hosts": hosts,
                                   "send": [0],
                                   "recv": [0],
                                   "duplex": [0]}
                port_cnt = port_meta['recommended_ports']
                total_port_cnt += port_cnt
                if port_meta['separate_send_receive']:
                    channels[ch_nm]["send"] = [round(port_cnt / 2)]
                    channels[ch_nm]["recv"] =\
                        [port_cnt - channels[ch_nm]["send"][0]]
                else:
                    channels[ch_nm]["duplex"] = [port_cnt]
            return (total_port_cnt, channels)

        def init_ports(p_port_cnt):
            """Get list of available ports"""
            ports = list()
            lo_port = FI.S['channels']['resources']['ports']['low']
            net_stat_tcp = ok, result = SI.run_cmd(["netstat -lant"])
            net_stat_udp = ok, result = SI.run_cmd(["netstat -lanu"])
            while len(ports) < p_port_cnt:
                for port in range(lo_port, lo_port + p_port_cnt + 1):
                    if port in net_stat_tcp or port in net_stat_udp:
                        print(f"Port {str(port)} is in use")
                    elif port not in ports:
                        ports.append(port)
            return ports

        def assign_ports(channels, ports):
            """Assign ports to channels"""
            print("Setting Unix firewall rules for game ports...")
            for nm, ch_meta in channels.items():
                for port_typ in ["duplex", "send", "recv"]:
                    for _ in range(0, ch_meta[port_typ][0]):
                        port = ports.pop(0)
                        # ok, result = SI.run_cmd(f"ufw delete allow {port}")
                        # Do I need to allow OUT as well as IN?
                        ok, result = SI.run_cmd(f"ufw allow {port}")
                        if ok:
                            channels[nm][port_typ].append(port)
                        else:
                            raise Exception(f"{FI.T['err_cmd']} {result}")
                    channels[nm][port_typ].pop(0)
            ok, result = SI.run_cmd("ufw reload")
            if ok:
                print(result)
                ok, result = SI.run_cmd("ufw enable")
            if ok:
                print(result)
                ok, result = SI.run_cmd("ufw status numbered")
                if ok:
                    print(result)
            if not ok:
                raise Exception(f"{FI.T['err_cmd']} {result}")
            return channels

        # set_channels main:
        # ==================
        hosts = get_host_IPs()
        total_port_cnt, channels = init_channels()
        ports = init_ports(total_port_cnt)
        channels = assign_ports(channels, ports)
        return channels

    def set_topics(self, channels):
        """Set topic info based on schema metadata

        @DEV:
        - Fire up an instance of saskan_server for each channel.
        - Figure out if "/queue" is appropriate for a send toapic or
          only for receives
        """

        def set_topic_name(ch_nm, brk_typ, brk_meta, channels):
            """Set topic name based on channel name, broker and traffic type"""
            for trf_typ in brk_meta['traffic']:
                topic_nm = f"/{ch_nm}/{brk_typ}/{trf_typ}"
                if brk_typ in ("broadcast",
                               "publish_subscribe",
                               "recipient_list"):
                    topic_nm = "/queue" + topic_nm
                if len(channels[ch_nm]["duplex"]["ports"]) > 1:
                    channels[ch_nm]["duplex"]["topics"].append(topic_nm)
                else:
                    channels[ch_nm][trf_typ]["topics"].append(topic_nm)
            return channels

        # set_topics main:
        # ================
        for ch_nm in channels.keys():
            for trf_typ in ("send", "recv", "duplex"):
                channels[ch_nm][trf_typ] = {"ports": channels[ch_nm][trf_typ],
                                            "topics": []}
                channels[ch_nm]["desc"] = {}
        for ch_nm, topic_meta in FI.S["topics"].items():
            for brk_typ, brk_meta in topic_meta.items():
                channels = set_topic_name(ch_nm, brk_typ, brk_meta, channels)
                channels[ch_nm]["desc"][brk_typ] = brk_meta["description"]
        FI.write_file(path.join(self.APP, FI.D['ADIRS']['CFG'],
                                "s_channels.json"), json.dumps(channels))

    def start_servers(self):
        """Start a saskan_server instance for each channel"""
        pypath = path.join(self.APP, FI.D['ADIRS']['PY'])
        logpath = path.join(FI.D['MEM'], FI.D['APP'],
                            FI.D['ADIRS']['SAV'], FI.D['NSDIRS']['LOG'])
        channels_cfg =\
            path.join(self.APP, FI.D['ADIRS']['CFG'], "s_channels.json")
        ok, err, channels_j = FI.get_file(path.join(channels_cfg))
        if ok:
            channels = json.loads(channels_j)
        else:
            raise Exception(f"{FI.T['err_file']} {err} {channels_cfg}")
        # pp(("channels", channels))
        for ch_nm, ch_meta in channels.items():
            host = ch_meta["hosts"][len(ch_meta["hosts"]) - 1]
            for trf_typ in ("send", "recv", "duplex"):
                for port in ch_meta[trf_typ]["ports"]:
                    svc_nm = f"/{ch_nm}/{trf_typ}:{port}"
                    cmd = ("nohup python -u " +
                           f"{pypath}/sv_server.py " +
                           f"'{svc_nm}' {host} {port} > " +
                           f"{logpath}/sv_server_" +
                           f"{svc_nm.replace('/', '_')}.log 2>&1 &")
                    try:
                        # print(f"Trying: {cmd} on {host}:{port}")
                        # Before bringing up the server, see if it is
                        # already running. If so, kill it.
                        # Do "ps -ef | grep sv_server", get the pid, kill it
                        # See io_shell:stop_running_services()
                        os.system(cmd)
                        # sleep(0.5)
                    except Exception as e:
                        raise Exception(f"{FI.T['err_cmd']} {e} {cmd}")
        ok, result = SI.run_cmd("ps -ef | grep sv_server")
        if ok:
            print(result)
        else:
            raise Exception(f"{FI.T['err_cmd']} {result}")


if __name__ == '__main__':
    SI = SaskanInstall()
