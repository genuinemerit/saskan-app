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
# import json
# import os

from os import path
from pathlib import Path
from pprint import pprint as pp     # noqa: F401
# from time import sleep

from io_file import FileIO          # type: ignore
from io_shell import ShellIO        # type: ignore
from saskan_report import SaskanReport  # type: ignore

FI = FileIO()
SI = ShellIO()
SR = SaskanReport()


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
        port_cnt, svc = self.init_svc_config()
        svc = self.set_ports_config(port_cnt, svc)
        svc = self.set_topics_config(svc)
        pp((svc))
        FI.pickle_saskan(self.APP)
        self.start_servers(svc)
        # self.start_clients()

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

    def init_svc_config(self):
        """Initialize svc config dictionary.
        Start by identifying how many ports need to be allocated
        for each traffic-type (send, receive or duplex) in channel
        """
        port_cnt = 0
        svc = dict()
        for c_nm, c_meta in FI.S['channel']['name'].items():
            port_cnt += c_meta['port_cnt']
            svc[c_nm] = {"host": FI.S['channel']['resource']['host']}
            if c_meta["duplex"]:
                svc[c_nm]["duplex"] = c_meta['port_cnt']
            else:
                svc[c_nm]["send"] = round(c_meta['port_cnt'] / 2)
                svc[c_nm]["recv"] = c_meta['port_cnt'] - svc[c_nm]["send"]
        return (port_cnt, svc)

    def set_ports_config(self, p_port_cnt, svc):
        """Get list of available ports using netstat to identify
        active TCP and UDP ports. Assign selected ports to svc config.
        N.B. "ALLOW IN" means that the port allows both outgoing and
        inbound transmission. Default is to allow OUT, deny IN. So
        adding ALLOW IN is necessary to allow inbound transmission.
        For a more sophisticated firewall, we'd probably assign
        exactly what IPs are allowed IN (and maybe OUT). For example,
        if all my clients use a specific set of IPs (and ports). For
        the current prototype, everything is on the a single monolith,
        so it doesn't matter.
        """
        print("Selecting ports and setting firewall for game ports...")
        ports = list()
        port = FI.S['channel']['resource']['port_low']
        ok, net_stat_result = SI.run_cmd(["netstat -lantu"])
        while len(ports) < p_port_cnt:
            if str(port) not in net_stat_result:
                ports.append(port)
            port += 1
        for c_nm, c_meta in svc.items():
            for p_typ in [pt for pt in c_meta.keys() if pt != "host"]:
                port_cnt = c_meta[p_typ]
                svc[c_nm][p_typ] = {"port": []}
                for _ in range(0, port_cnt):
                    port = ports.pop(0)
                    ok, result = SI.run_cmd(f"ufw allow in {port}")
                    if ok:
                        svc[c_nm][p_typ]["port"].append(port)
                    else:
                        raise Exception(f"{FI.T['err_cmd']} {result}")
        ok, result = SI.run_cmd("ufw reload")
        if ok:
            print(result)
            ok, result = SI.run_cmd("ufw enable")
        if ok:
            print(result)
        if not ok:
            raise Exception(f"{FI.T['err_cmd']} {result}")
        return svc

    def set_topics_config(self, svc):
        """Set service config based on topic and broker-type metadata
        """
        for c_nm, c_meta in svc.items():
            for p_typ in [pt for pt in c_meta.keys() if pt != "host"]:
                svc[c_nm][p_typ]["topic"] = {}
            svc[c_nm]["desc"] = {}
        for c_nm, t_meta in FI.S["topic"].items():
            for t_nm, b_meta in t_meta.items():
                svc[c_nm]["desc"][t_nm] = b_meta["desc"]
                for d_typ in b_meta['direction']:
                    if "duplex" in svc[c_nm].keys():
                        topic_nm = t_nm + "_" + d_typ
                        d_typ = "duplex"
                    else:
                        topic_nm = t_nm
                    svc[c_nm][d_typ]["topic"][topic_nm] = {"action": {}}
        return svc

    def start_servers(self, svc):
        """Start a saskan_server instance for each channel.
        The server module receives messages from clients, sends them
        to message gateway (backend processors), which is turn sends
        links or fail messages to clients.

        :Args:
        - svc: service config dictionary
        """
        pgm_nm = "sv_server"
        SI.kill_jobs(pgm_nm)
        # Launch new sv_server instances
        pypath = path.join(self.APP, FI.D['ADIRS']['PY'], f"{pgm_nm}.py")
        logpath = path.join(FI.D['MEM'], FI.D['APP'],
                            FI.D['ADIRS']['SAV'], FI.D['NSDIRS']['LOG'])
        for c_nm, c_meta in svc.items():
            for p_typ in [pt for pt in c_meta.keys()
                          if pt not in ("host", "desc")]:
                for port in c_meta[p_typ]["port"]:
                    SI.run_nohup_py(pypath,
                                    logpath,
                                    f"/{c_nm}/{p_typ}:{port}",
                                    c_meta['host'],
                                    port,
                                    pgm_nm)
        result, _ = SR.rpt_jobs(pgm_nm)
        print("Servers started or restarted:")
        print(result)

    def start_clients(self):
        """Start a saskan_request instance for each plan + client-type.
        Note that "requestors" need to be renamed to "clients".
        They do more than send requests; they also take some kind of
        functional action based on the response message. Modify wiki
        and code accordingly. The "request" handlers should be named
        like *_client.py, not *_request.py. In some more complex cases
        I may find that *_client_request and *_client_response_handler
        need to be separated too. Keep it consolildated to start with.

        The client modules can be "brokers" in the sense that they
        might be used by more than one application-level GUI or CLI or
        business logic module. Might think of the client module as the
        "front end traffic cop". (*_reponse.py modules are the "back end"
        traffic handlers, and I suppose the *_server.py modules could be
        referred to as the "middleware managers".)

        There are (so far) 3 types of clients:
        - transactional: one-one txns, a caller triggers it & handles reply,
            which is targeted to that specific client

        - polling: send multiple copies of the reply to a subscriber list.
            Of which there are two sub-flavors, which have to do mainly with
            how a client gets on the subscriber list. The underlying mechanisms
            are similar. Broadcast is like a simpler version of pub-sub.

            - broadcast: subscribers are identified by a system configuration
                setting and it is a fairly static subscriber list.

            - publish-subscribe: subscribers are identified by request messages
                (subscribe requests) and are more dynamic. Subs may have an
                expiration limit. Subs may be "one-shot" or "recurring". There
                is an "unsubscribe" option.

        - event-driven: a chain of transactional clients, where each request
            is triggered by a previous response. The first request is sent by
            a regular transactional client, then a chain of events rolls out.
            Sort of like an ETL pipeline.  Can trigger other txns, polling, or
            both.

        A client-type can be both transactional and event-driven.
        Or polling and event-driven.
        It would be odd to be only event-driven, but maybe it could happen.

        ===

        Maybe update the service config file ("s_channels.json" for now...
        should be renamed to "s_services.json") to include a "clients" section
        or something. The next level of meta-data will be the "plans".

        A plan defines:
        - actions, which consist of an action name and a set of one to many
          event names associated with a topic. The events  have either
          "request" or "reponse" in their name.  In  JSON file, associate them
          with a send or receive channel respectively. (Not 100% sure about
          that, but it seems to make sense for now.)  If the channel for that
          topic is duplex, then all the actions/events are associated with a
          single channel and send/receive is designated by the topic name.
        - Optionally, a set of triggers associated with an action. These are
          used to define the chain of events for event-driven clients. The
          trigger identifies what topic + plan(s) trigger the action.
        """
        def update_service_meta(svc: dict):
            """Update service meta-data with action/event information.

            @DEV:
            With respect to designing the client modules:
            - Action/event is only the high level. Like "what actions
              are supported by this module".
            - The client module will also need to...
                - handle specific message structures for each action/event.
                - listen for, handle a response message, which is a link to a
                Harvest message, a simple ack, or an error message.
            - Not sure if this can all be genericized completely, i.e.,
              probably using pickled objects to define the events and messages,
              or if I'll need a collection of python modules -- possibly auto-
              generated ones.
            - Even if I can generecize the client.py, will still want to
              have multiples instances in all likelihood. Need to think about
              that. Having dedicated ports might help; may or may not want to
              use the same ones that the server.py's are using? Or is this more
              like just need a bunch of them available round-robin style, maybe
              served up on a Nginx or twisted server?

            For now, continue to generate  consolidated services meta-config,
            which can be pickled and should provide prototype for
            how any message should be handled.
            """
            def set_event_typ(p_meta):
                e_typ = ""
                if "transactional" in p_meta['client_type']:
                    e_typ += "txn_"
                if "polling" in p_meta['client_type']:
                    e_typ += "poll_"
                if "event-driven" in p_meta['client_type']:
                    e_typ += "event_"
                return e_typ[:-1]

            def set_actions(svc, p_meta, action_nm,
                            c_typ, s_top_nm, e_typ):
                svc[c_nm][c_typ]["topics"][s_top_nm]["action"][action_nm] = []
                for event_nm in p_meta['action'][action_nm]:
                    if (("response" in event_nm and
                            (c_typ == "send" or "send" in s_top_nm)) or
                        ("request" in event_nm and
                            (c_typ == "recv" or "recv" in s_top_nm))):
                        svc[c_nm][c_typ]["topics"][s_top_nm]["action"][action_nm].append(  # noqa: E501
                            e_typ + "_" + event_nm)
                return svc

            for p_top_nm, p_meta in FI.S['plans'].items():
                c_nm = p_top_nm.split('/')[1]
                e_typ = set_event_typ(p_meta)
                for action_nm in p_meta['action'].keys():
                    for c_typ in ("duplex", "recv", "send"):
                        for s_top_nm in svc[c_nm][c_typ]["topics"].keys():
                            svc = set_actions(svc, p_meta, action_nm,
                                              c_typ, s_top_nm, e_typ)

            return svc

        # ====================
        # start_clients (main)
        # ====================
        svc = update_service_meta(self.get_svc_meta_file())
        pp(svc)


if __name__ == '__main__':
    SI = SaskanInstall()
