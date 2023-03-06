#!python
"""Saskan Apps file configuration / install / set-up.
:module:    saskan_install.py
:class:     SaskanInstall/0
:author:    GM <genuinemerit @ pm.me>

Requires sudo privs to execute properly.
Writes bash files to /usr/local/bin
Launch it by running sudo ./saskan_install from the git project directory,
using the "saskan" conda environment.
e.g. (saskan) ~/../Saskantinon/saskan_install

@DEV:
- Add/test install of scenes.json in schema.
- Prototype/test using haproxy to load balance servers.
- Simplify the proliferation of ports. I shouldn't need so many.
"""
import json

# import os

from os import path
from pathlib import Path
from pprint import pprint as pp  # noqa: F401

# from time import sleep

from io_file import FileIO  # type: ignore
from io_shell import ShellIO  # type: ignore
from io_wiretap import WireTap  # type: ignore
from saskan_report import SaskanReport  # type: ignore

FI = FileIO()
SI = ShellIO()
SR = SaskanReport()
WT = WireTap()


class SaskanInstall(object):
    """Configure and install set-up for Saskan apps.

    Bootstrap config and schema metadata from project directory.
    Use current working directory (git project) to derive home directory.

    @DEV:
    - Create servers, clients, queues, load balancers and so on.
    - Save updated svc dict to a config file, then pickle it.
    """

    def __init__(self):
        """Initialize directories and files."""
        self.verify_bash_bin_dir()
        self.APP = path.join("/home", Path.cwd().parts[2], FI.D["APP"])
        self.create_app_space()
        self.install_app_files()
        self.copy_python_scripts()
        self.copy_bash_files()
        self.set_ports()
        self.save_svc_config()
        self.create_load_bals()
        self.install_load_bals()
        # self.start_servers(svc)
        # self.start_clients()
        # FI.pickle_saskan(self.APP)

    # Helpers
    # ==============================================================

    def verify_bash_bin_dir(self):
        """Verify standard bash directory exists.
        - /usr/local/bin
        """
        files = FI.get_dir(FI.D["BIN"])
        if files is None:
            raise Exception(f"{FI.T['err_file']} {FI.D['BIN']}")

    # Directory, file, record set-up
    # ==============================================================

    def create_app_space(self):
        """If app dir already exists, delete everything.
        Create sakan app directory.
        Create sakan app sub-dirs.
        Create namesapce sub-dirs.
        """
        # App dir
        files = FI.get_dir(self.APP)
        if files is not None:
            # Delete everything in app dir
            app_files = self.APP + "/*"
            ok, result = SI.run_cmd([f"sudo rm -rf {app_files}"])
            if not ok:
                raise Exception(f"{FI.T['err_process']} {result}")
            ok, result = SI.run_cmd([f"sudo rmdir {self.APP}"])
            if not ok:
                raise Exception(f"{FI.T['err_process']} {result}")
        FI.make_dir(self.APP)
        FI.make_executable(self.APP)
        # App sub-dirs
        for _, sub_dir in FI.D["ADIRS"].items():
            sdir = path.join(self.APP, sub_dir)
            FI.make_dir(sdir)
            FI.make_executable(sdir)
        # Namespace sub-dirs
        for _, sub_dir in FI.D["NSDIRS"].items():
            sdir = path.join(self.APP, FI.D["ADIRS"]["SAV"], sub_dir)
            FI.make_dir(sdir)
            FI.make_executable(sdir)
            FI.make_writable(sdir)

    def install_app_files(self):
        """Copy config, image and schema/ontology files"""
        for sdir in (FI.D["ADIRS"]["CFG"],
                     FI.D["ADIRS"]["IMG"],
                     FI.D["ADIRS"]["ONT"]):
            src_dir = path.join(Path.cwd(), sdir)
            files = FI.get_dir(src_dir)
            if files is not None:
                FI.copy_files(path.join(self.APP, sdir), files)

    def copy_python_scripts(self):
        """Copy - python (*.py) files --> /python
        Excluding installer scripts.
        """
        files = FI.get_dir(Path.cwd())
        if files is None:
            raise Exception(f"{FI.T['err_file']} {Path.cwd()}")
        py_files = [
            f for f in files if str(f).endswith(".py") and
            "_install" not in str(f)
        ]
        tgt_dir = path.join(self.APP, FI.D["ADIRS"]["PY"])
        for f in py_files:
            if Path(f).is_file():
                tgt_file = path.join(tgt_dir, str(f).split("/")[-1])
                FI.copy_file(str(f), tgt_file)

    def copy_bash_files(self):
        """Copy /bash to /usr/local/bin

        Set up the command-line exectuables for saskan.
        Modify before copying to correctly locate the
        python files in the saskan app directory.
        """
        src_dir = path.join(Path.cwd(), "bash")
        py_dir = path.join(self.APP, FI.D["ADIRS"]["PY"])
        files = FI.get_dir(src_dir)
        for bf in files:
            bf_name = str(bf).split("/")[-1]
            tgt_file = path.join(FI.D["BIN"], bf_name)
            bf_code = FI.get_file(str(bf))
            if bf_code is None:
                raise Exception(f"{FI.T['err_file']} {bf}")
            bf_code = bf_code.replace("~APP_DIR~", py_dir)
            FI.write_file(tgt_file, bf_code)
            FI.make_executable(tgt_file)

    def get_free_ports(self, p_next_port: int, p_req_port_cnt: int) -> tuple:
        """Get a set of free ports
        :args:
        - next_port: next port to check
        - p_req_port_cnt: number of ports to allocate
        :return: (list: assigned ports,
                  int: next port number to check)
        """
        # print(f"Selecting {p_req_port_cnt} ports starting at {p_next_port}")
        _, net_stat_result = SI.run_cmd(["netstat -lant"])
        ports: list = list()
        while len(ports) < p_req_port_cnt:
            if (
                str(p_next_port) not in net_stat_result
                and str(p_next_port) not in ports
            ):
                ports.append(p_next_port)
            p_next_port += 1
        return (ports, p_next_port)

    def set_firewall(self, p_ports: list):
        """
        Set firewall rules for each port.
        :args:
        - p_ports: list of port numbers to configure
        :updates: UFW Unix firewall rules

        "ALLOW IN" means that the port allows both outgoing and
        inbound transmission. Default is to allow OUT, deny IN. So
        adding ALLOW IN is necessary to allow inbound transmission.
        For a more sophisticated firewall, we'd probably assign
        exactly what IPs are allowed IN (and maybe OUT). For example,
        if all my clients use a specific set of IPs (and ports).
        For now, it would be overkill.
        """
        print("Reset all firewall rules...")
        ok, result = SI.run_cmd("ufw reset")
        print(f"Set firewall rules for {len(p_ports)} ports...")
        if ok:
            for port in p_ports:
                ok, result = SI.run_cmd(f"ufw allow in {port}")
                if not ok:
                    raise Exception(f"{FI.T['err_cmd']} {result}")
            print("Enable new firewall rules...")
            ok, result = SI.run_cmd("ufw enable")
            if ok:
                print(result)
        if not ok:
            raise Exception(f"{FI.T['err_cmd']} {result}")

    def set_ports(self):
        """
        Assign ports for services, peers and routers.

        :updates:
        - firewall rules
        - service configuration metadata
        """
        all_ports: list = list()
        next_port = FI.S["resource"]["port_low"]
        for svct, svci in (("channels", "channel"),
                           ("peers", "client"),
                           ("peers", "router")):
            for svcn in (FI.S[svct][svci]).keys():
                if "port" in (FI.S[svct][svci][svcn]).keys():
                    for portn in FI.S[svct][svci][svcn]["port"].keys():
                        if ("count" in
                                FI.S[svct][svci][svcn]["port"][portn].keys()):
                            portc =\
                                FI.S[svct][svci][svcn]["port"][portn]["count"]
                            ports, next_port =\
                                self.get_free_ports(next_port, portc)
                            FI.S[svct][svci][svcn]["port"][portn]["num"] =\
                                ports
                            all_ports += ports
        self.set_firewall(all_ports)

    def save_svc_config(self):
        """Save service config data to a file."""
        cdir = path.join(self.APP, FI.D["ADIRS"]["CFG"], "m_svc.json")
        FI.write_file(cdir, json.dumps(FI.S))

    def create_load_bals(self):
        """Create one or more NGINX load balancer config files.
        Store them in the saskan app /config directory.

        :write: load balancer config files

        @DEV:
        - Read up on the various options for NGINX load balancing.
        - Eventually want add SSL/letsencrypt support.
        - Include comments in the NGINX files.
        """
        host = FI.S["resource"]["host"]
        lb_confs: list = list()
        for svct, svci in (("channels", "channel"),
                           ("peers", "client"),
                           ("peers", "router")):
            for svcn in (FI.S[svct][svci]).keys():
                if "port" in (FI.S[svct][svci][svcn]).keys():
                    lbx = 0
                    ports = FI.S[svct][svci][svcn]["port"]
                    conf = "stream {\n"
                    for porttyp in ("send", "recv", "duplex", "polling"):
                        if porttyp in ports.keys():
                            conf += "\n\tupstream " +\
                                    f"{svcn}_{porttyp} {{\n" +\
                                    "\t\tleast_conn;\n"
                            for p in ports[porttyp]["num"]:
                                conf += f"\t\tserver {host}:{p} weight=10;\n"
                            conf += "\t}\n"
                            conf += "\n\tserver {\n" +\
                                    "\t\tlisten " +\
                                    f"{ports['load_bal']['num'][lbx]};\n" +\
                                    f"\t\tproxy_pass {svcn}_{porttyp};\n" +\
                                    "\t}\n"
                            lbx += 1
                    conf += "}\n"
                    lb_confs.append(path.join(self.APP, FI.D["ADIRS"]["CFG"],
                                              f"saskan_lb_{svcn}.conf"))
                    FI.write_file(lb_confs[-1:][0], conf)

    def install_load_bals(self):
        """
        Back up old nginx.conf file, then copy new one to /etc/nginx.
        Make sure /etc/nginx/streams.conf.d exists.
        Deploy saskan stream config files to /etc/nginx/streams.conf.d.
        Reboot nginx.

        Commands to use:
        - sudo service nginx status
        - sudo systemctl enable nginx  <-- may only need once
        - nginx -s reload
        - service nginx restart

        - the basic nginx.conf file has no tcp or stream sections.
        - tried goofing around with it to no avail
        - time to go read a book I guess. argh.
        - pretty much just emptied out the nginx.conf file and it liked that!
        - nginx -t    <-- to test config

        - maybe i need to open port 80?

        - trying to do this under a virtual ubuntu set-up on my mac.
        - maybe look around at some older code, see how it is set up
          on digital ocean, etc. Maybe start a fresh nginx install.
        - also might want to try twisted instead.
        - or look for new/other python libraries for this.

        - Seems better after reinstalling nginx using instructions from
        "NGINX Cookbok", 2nd edition, by Derek DeJonghe.

        Stop all saskan NGINX servers.
        Start the saskan NGINIX load balanceers.

        (base) bow@mahaka:~$ sudo nginx -v
nginx version: nginx/1.18.0 (Ubuntu)
(base) bow@mahaka:~$ ps -ef | grep nginx
root        1508       1  0 18:40 ?        00:00:00 nginx: master process
    /usr/sbin/nginx -g daemon on; master_process on;
www-data    1517    1508  0 18:40 ?        00:00:00 nginx: worker process
www-data    1518    1508  0 18:40 ?        00:00:00 nginx: worker process
root        5106    2500  0 18:45 ?        00:00:00 nginx: master process nginx
www-data    5107    5106  0 18:45 ?        00:00:00 nginx: worker process
www-data    5108    5106  0 18:45 ?        00:00:00 nginx: worker process

        @DEV:
        - Oher clean up tasks:
            - remove old load balancer links
            - remove old load balancer config files
            - probably want a bespoke nginx.conf file for saskan
            - it is recommended to use /etc/nginx/conf.d/ not
              sites-enabled/sites-available so try that
            - will eventually want to use letsencrypt for SSL,
              possibly other security things
            - don't think it's including my config files now
            - try enabling the default config file, see if my
              tcp stuff works then
        - Ah-ha! See chapter 2.2 of the book
            - create a stream.conf.d directory
            - in nginx.conf:
            stream {
                include /etc/nginx/stream.conf.d/*.conf;
            }
            - put my stream config files in there;
              they don't need to have the "stream {" and "}" containers
            'NGINX Plus' provides more TCP load balancing features.
        - That is the book I've been looking for. It covers TCP and UDP
          as well as HTTP.

        - Read in the config files from app confitg dir.


        After following the directions in the book, I am still not
        having success with TCP load balancing using NGINX. It may
        just be my local environment that is funky. Maybe try it again
        on Digital Ocean just to confirm if it works there are not.

        In the meantime, I think I will try using HAProxy instead.

        There is a Load Balancer service on Digital Ocean that
        works with balancing "Droplets", which would refer to entire
        Linux (or other) OS-level nodes. I think it can create
        forwarding rules at the port level too? Might want to look
        into it, for learning purposes if nothing else. It is a paid/
        monthly subscription service, though.
        """
        ng_d = "/etc/nginx"
        FI.copy_file(path.join(ng_d, "nginx.conf"),
                     path.join(ng_d,
                               f"nginx_conf.bkup.{WT.get_iso_timestamp()}"))
        FI.copy_file(path.join(self.APP, FI.D["ADIRS"]["CFG"], "nginx.conf"),
                     ng_d)
        FI.make_dir(path.join(ng_d, "stream.conf.d"))
        for cfg_p in [f for f in
                      FI.get_dir(path.join(self.APP, FI.D["ADIRS"]["CFG"]))
                      if "saskan_lb_" in str(f) and ".conf" in str(f)]:
            FI.copy_file(cfg_p, path.join(ng_d, "stream.conf.d"))
        # available = path.join("/etc/nginx/sites-available")
        # enabled = path.join("/etc/nginx/sites-enabled")
        # for lbc in p_lb_confs:
        #     lbc_file_nm = path.basename(lbc)
        #     FI.copy_file(lbc, available)
        #     FI.make_link(path.join(available, lbc_file_nm),
        #                 path.join(enabled, lbc_file_nm))

    def start_servers(self, svc):
        """Start a saskan_server instance for each channel.
        The server module receives messages from clients, sends them
        to router , which sends them to a message gateway (backend processors),
        which is turn sends links to reply packages, or fail messages, or
        ack messages to clients (via the message broker/server if I'm not
        mistaken).

        The way these are set up, there are multiple instances of some
        channels, but each resides on a different port. So, not a load
        balancing kind of thing per se, with round-robin launches of servers,
        just "twin" (or "triplet" or whatever) servers on different ports.

        Not sure how this gets handled, actually. How does the client
        "know" which port to connect to? Is it a random choice? Or is
        there in fact some kind of load balancing needed "in front of"
        the ports. Do I do that with Nginx or twisted? Or is it
        already being handled by asyncio? Not sure yet...

        Since the server/message broker activity is pretty generic, there
        is a single python server module, saskan_server.py, which gets
        launched multiple times, sending it parameters relevant to the
        channel (topics) it is handling.

        'run nohup' means it will run in the background, and will not
        write to the terminal. The output gets written to a log file.

        So far, it looks to me like the servers I have expect a "subscriber"
        model, where a message is simply bounced to a specified list of
        "listeners" (e.g. the SUBSCRIBERS)? The channels are associated with
        "responders" (routers, which then call gateways), which in turn
        send replies to intended for a subscriber list, which this time
        are the appropriate clients. As I'm understanding it, the server
        actually does the routing, and the clients are just "listeners"
        when they are not sending requests.

        Not sure that distinct send/receive servers is useful. A server
        gets peers ("subscribers" -- "who will I send msgs to?"), reads
        msgs from them, and sends them to a responder (router), which
        in turn sends them to a gateway, which in turn sends them back
        to the server, which in turn sends them to the appropriate
        client-subscriber. Both respoders and clients are "peers". The
        server has to both send and receive. I am thinking a one-directional
        pipe is only useful if the server itself is a "broadcaster" or
        perhaps a "logger", that is, the traffic iteself is only one-way.

        I'm also thinking that the (duplex) ports assigned to a channel
        DO need to be behind a proxy, so that the channel (server) can
        be load balanced.

        For TCP load balancing with Nginx see online article (bookmarked)
        and example code in lab/service_lab/gallery_bal_56089.conf. That
        is for http/https, but I think it will work with TCP as well.
        Not sure if I really need to buy Nginx Plus for it to work.
        If so, maybe look at using twisted instead.

        :Args:
        - svc: service config dictionary
        """
        pgm_nm = "sv_server"
        SI.kill_jobs("/" + pgm_nm)
        # Launch new sv_server instances
        pypath = path.join(self.APP, FI.D["ADIRS"]["PY"], f"{pgm_nm}.py")
        logpath = path.join(
            FI.D["MEM"], FI.D["APP"],
            FI.D["ADIRS"]["SAV"], FI.D["NSDIRS"]["LOG"]
        )
        for c_nm, c_meta in svc.items():
            for p_typ in [pt for pt in c_meta.keys()
                          if pt not in ("host", "desc")]:
                for port in c_meta[p_typ]["port"]:
                    SI.run_nohup_py(
                        pypath,
                        logpath,
                        f"/{c_nm}/{p_typ}:{port}",
                        c_meta["host"],
                        port,
                        pgm_nm,
                    )
        result, _ = SR.rpt_running_jobs("/" + pgm_nm)
        print("Servers (message brokers) started or restarted:")
        print(result)

    def start_clients(self, svc):
        """Start a 'saskan_client' instance for each plan + client-type.
        Cleints initiate actions and also take a functional followup,
        which may involve a subsequent message, based on responses.
        In some more complex cases it may be useful
        to separate *_client_request and *_client_response_handler
        modules. Keep it consolildated to start with.

        Client modules are "brokers" in that they can be called by more
        than one app-level GUI or game logic module.

        There are (so far) 3 types of clients:
        - transactional: one-one txns, a client triggers an action & handles
        the reply, which is honed for that specific client

        - polling: send multiple copies of a reply to a subscriber list.
          Two sub-flavors, which relate to how subscriber list is managed:

            - publish-subscribe: subscribers identified by request messages
                (subscriber requests) and are dynamic. Subs may have an
                expiration limit, may be "one-shot", or "recurring". There
                is an "unsubscribe" option.
            - broadcast: subscribers identified by a system configuration
                setting; a mostly static subscriber list.
                Broadcast is like a simpler version of pub-sub.

        - event-driven: chain of transactional clients, each request triggered
          by a previous response. First request in chain sent by regular
          transactional client, then a chain of events rolls out.
          Like an ETL pipeline.  Can trigger other txns, polling, or both.

        Client-type can be transactional and event-driven.
        Or polling and event-driven.
        It would be odd to be only event-driven, but maybe it could happen.

        ===
        A plan defines:

        - actions, which consist of an action name and a set of one to many
          event names associated with a topic. The events have either
          "request" or "response" in their name.  In svc config, associate them
          with a send or receive channel respectively. If channel is duplex,
          then all the actions/events are associated with a single channel;
          so send/receive are designated by the topic name.

        - Optionally, an action can have a set of triggers. They define the
          chain of events for event-driven clients, i.e., what topic + plan(s)
          (can) trigger the action.

        @DEV:
        With respect to designing the client modules:
        - Action/event is only the high level. Like "what actions
            are supported by this module".
        - The client module _also_ needs to...
            - handle specific message structures for each action/event.
            - listen for, handle a response message, which is a link to a
            Harvest message, a simple ack, or an error message.
        - Not sure if this can all be genericized completely, i.e.,
            probably using pickled objects to define the events and messages,
            or if I'll need a collection of python modules -- possibly auto-
            generated ones.
        - Even if I can genericize the client.py, likely still want/need
            multiples instances. Need to think about that.
            Having dedicated ports for clients might help.  May want to
            use the same ones that the server.py's are using. Or not.
            May want a bunch of them available round-robin style on the
            same port, maybe served up on a Nginx or twisted server?

        For now, continue to generate consolidated svc meta-config,
        which can be pickled and should provide prototype/basics for
        how any message should be handled. If that ends up getting
        hard-coded by generating python modules, it may not be necessary.

        Stick with plain-vanilla asyncio based modules for now.
        Once feeling good about it, maybe try another library like Trio
        and / or use one of those AI coders to generate the modules.
        See OpenAI and ChatGPT here: https://openai.com/api/
        """
        pass

    def start_responders(self, svc):
        """
        Should be sufficient metadata in svc to generate modules or
        instances of modules for each needed router and messaging
        gateway. The router simply routes incoming requests to the
        appropriate gateway, which then does backend work to craft a
        response message, writes the message to the Harvest namespace,
        and then responds to the server (message broker) with either
        a link to the Harvest reccord, or a simple ack, or an error.

        As with clients, not sure if I need ports devoted to the routers
        and gateways. Probably yes. And if I need mulitple instances
        of each, that is, some kind of load balancing.  Probably yes.
        """
        pass


if __name__ == "__main__":
    SI = SaskanInstall()
