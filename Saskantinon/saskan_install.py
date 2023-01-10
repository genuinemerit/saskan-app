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

    Bootstrap config and schema metadata from project directory.
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
        svc = self.set_channels(dict())
        svc = self.set_topics(svc)
        # svc = self.set_plans(svc)
        # svc_about = self.set_descs(svc_about)
        # svc_msgs = self.set_msgs()
        pp((svc))
        # pp((svc_d))
        # pp((svc_about))
        # pp((svc_msgs))
        # FI.pickle_saskan(self.APP)
        # self.start_servers(svc)
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

    def set_hosts_and_port_cnt(self,
                               p_meta_nm: str,
                               p_svc: dict):
        """
        :args:
        - p_meta: str: name of metadata schema for broker or peer
        - p_svc: dict: service config data
        :return: tuple:(int: msg broker ports for all channels,
                        dict: persisted config metadata)

        Identify host(s), how many message broker service ports needed
        for each traffic-type (send, receive or duplex).
        For each type, add one more port for load balancing.
        """
        port_cnt = 0
        p_svc[p_meta_nm] = dict()
        for m_nm, m_meta in FI.S[p_meta_nm]['name'].items():
            p_svc[p_meta_nm][m_nm] = {
                "host": FI.S[p_meta_nm]['resource']['host'],
                "ports": dict()}
            for p_typ, p_cnt in m_meta.items():
                port_cnt += p_cnt + 1
                p_svc[p_meta_nm][m_nm]['ports'][p_typ] = p_cnt
                p_svc[p_meta_nm][m_nm]['ports']["load_bal"] = 1
        return (port_cnt, p_svc)

    def set_ports(self,
                  p_next_port: int,
                  p_port_cnt: int,
                  p_ports: list = list()):
        """Get a list of free ports
        :args:
        - next_port: next port to check
        - p_port_cnt: number of ports to allocate
        - ports: list of ports already allocated
        :return: tuple: (list: assigned ports,
                         int: next port to check)
        """
        print("Selecting available ports...")
        _, net_stat_result = SI.run_cmd(["netstat -lant"])
        cur_port_cnt = len(p_ports)
        while len(p_ports) < (cur_port_cnt + p_port_cnt):
            if str(p_next_port) not in net_stat_result and\
               str(p_next_port) not in p_ports:
                p_ports.append(p_next_port)
            p_next_port += 1
        return (p_ports, p_next_port)

    def set_firewall(self,
                     p_meta_nm: str,
                     p_ports: list,
                     p_svc: dict):
        """
        Set firewall rules for each port.
        :args:
        - p_meta_nm: name of metadata schema for broker or peer
        - p_ports: list of port numbers to configure
        - p_svc: dict of service metadata
        :returns: dict: service metadata with ports assigned

        Assign ports to services in the order they appear in
        the svc config metadata.

        "ALLOW IN" means that the port allows both outgoing and
        inbound transmission. Default is to allow OUT, deny IN. So
        adding ALLOW IN is necessary to allow inbound transmission.
        For a more sophisticated firewall, we'd probably assign
        exactly what IPs are allowed IN (and maybe OUT). For example,
        if all my clients use a specific set of IPs (and ports). For
        the current prototype, it doesn't matter.
        """
        print("Setting firewall for ports...")
        for m_nm, m_meta in p_svc[p_meta_nm].items():
            for p_typ, p_cnt in m_meta["ports"].items():
                p_svc[p_meta_nm][m_nm]["ports"][p_typ] = list()
                for _ in range(0, p_cnt):
                    port = p_ports.pop(0)
                    ok, result = SI.run_cmd(f"ufw allow in {port}")
                    if not ok:
                        raise Exception(f"{FI.T['err_cmd']} {result}")
                    p_svc[p_meta_nm][m_nm]["ports"][p_typ].append(port)
        ok, result = SI.run_cmd("ufw reload")
        if ok:
            print(result)
            ok, result = SI.run_cmd("ufw enable")
            if ok:
                print(result)
        if not ok:
            raise Exception(f"{FI.T['err_cmd']} {result}")
        return p_svc

    def set_channels(self,
                     p_svc: dict):
        """Set hosts and ports for message brokers which manage
        a specific channel.
        :args: p_svc: dict: service metadata
        :returns: dict: service metadata
        """
        port_cnt, svc = self.set_hosts_and_port_cnt('channel', p_svc)
        ports, next_port = self.set_ports(
            FI.S['channel']['resource']['port_low'], port_cnt)
        p_svc["next_port"] = next_port
        svc = self.set_firewall('channel', ports, p_svc)
        return svc

    def set_topics(self,
                   p_svc):
        """Assign topics to channels.

        In my nomenclature, a "topic" is like a channel type,
        or a messaging pattern. For example, "request-reply" or
        "broadcast" or "publish-subscribe".

        :args: p_svc: dict: service config data
        :returns: dict: service config data
        """
        for m_nm in p_svc["channel"].keys():
            p_svc["channel"][m_nm]["topic"] = {}
            for t_nm, t_desc in FI.S["topic"][m_nm].items():
                p_svc["channel"][m_nm]["topic"][t_nm] = t_desc
        return p_svc

    def set_plans(self, svc):
        """
        In my terminology, a "plan" drills down on what type of peer
        uses a given topic, such as what types of client/peer activity
        are associated with the topic. A "peer" can refer to an "end user"
        client-broker, or to a backend gateway. Any modules that can send
        messages to and/or subscribe and receive messages from a message
        broker are "peers".  Client is a synonym, but sometimes is used
        to refer only to "front end" modules, so I like "peers" better
        for referencing at this more abstract level.

        Plan types include:

        - transactional: request-reply
          Two flavors:
          - One-to-one txns, peer triggers an action, handles reply,
            which is honed for that specific peer request
          - Event-driven, aka chained request: chain of transactions, each
            triggered by a previous response. First in chain is regular
            one-to-one, then a series of events may cascade. Sort of like
            an ETL pipeline.

        - polling: send multiple copies of a reply to a subscriber list.
          Two flavors, related to how subscriber list is managed:
            - publish-subscribe: subscriber list is dynamic, may have an
              expiration limit, may be one-shot, or recurring, can be
              unsubscribed from.
            - broadcast: subscriber list set by system config setting,
              is mostly static, like a simple preset version of pub-sub.

        - a mix of the above, such as a chain that includes both polling
          and subsequent transations.

        A plan defines:

        - actions: an action name + one to n event names.
        - events: associated with a send or recv channel if those are
          used in the channel associated with the topic, otherwise
          the events use a duplex channel. Typically events have names
          like "request_*" or "response_*".
          - "request" events become associated with "receive" channels,
            with messages sent to a channel by a client peer
            like a GUI, or a business logic module.
          - "response" events become associated with "send" channels,
            with messages sent to a channel by a backend gateway.
        - triggers: define the preceding event in a chain, named using
          the "full path" of a message: channel.topic.action.event

        @DEV:
        - the content-router calls backend "gate" modules, which go
          backend business logic, craft responses, post response msgs
          to ns_harvest.  The router interfaces with the channel and
          therefore will have multiple instances behind a load balancer.
        - client-peers ("front end") get triggered by a polling module,
          running under cron most likely. The actual "end user" modules
          don't send messages themselves, and there is no "calling" a
          transactional peer module. Instead, they write to a queue and
          the poller picks up the queue, crafts/sends a message to the
          peer, gets the response and writes back to the queue. Then the
          end-user program still has to poll the queue for responses.
          - The peer is a kind of "broker". If it is likely to be used
            alot, then there should be multiple instances behind a load
            balancer.
          - Likewise, a poller may serve multiple quuees, and should also
            be multiplexed, though whether it needs a load balancer is
            debatable.
        - Subscriptions will need to be sent to ALL instances of a given
          send or receive or duplex channel, so that the peer will get a
          reponse no matter which instance of the channel it is connected
          to.  OR, look into using a shared queue for subscribers. That might
          be better...  Whew!  Fun stuff! (Weird, but fun!)
        """
        def set_event_type(p_meta):
            e_typ = ""
            if "transactional" in p_meta['client_type']:
                e_typ += "txn_"
            if "polling" in p_meta['client_type']:
                e_typ += "poll_"
            if "event-driven" in p_meta['client_type']:
                e_typ += "event_"
            return e_typ[:-1]

        def set_events(c_nm, p_typ, t_nm, a_nm, events, svc):
            svc_action = svc[c_nm][p_typ]["topic"][t_nm]["action"]
            svc_action[a_nm] = {"event": []}
            for e_nm in events:
                if (("response" in e_nm and
                        (p_typ == "send" or "send" in t_nm)) or
                    ("request" in e_nm and
                        (p_typ == "recv" or "recv" in t_nm))):
                    svc_action[a_nm]["event"].append(e_typ + "/" + e_nm)
                elif (isinstance(e_nm, dict) and
                        list(e_nm.keys())[0] == "trigger"):
                    svc_action[a_nm]["trigger"] = e_nm["trigger"]
            return svc

        # set_plans:
        # ===================
        for p_nm, p_meta in FI.S['plan'].items():
            c_nm = p_nm.split('/')[0]
            t_nm = p_nm.split('/')[1]
            e_typ = set_event_type(p_meta)

            for a_nm in p_meta['action'].keys():
                events = p_meta['action'][a_nm]
                for p_typ in [pt for pt in svc[c_nm].keys()
                              if pt not in ["host", "desc"]]:
                    if "duplex" in svc[c_nm].keys():
                        for d_typ in ["send", "recv"]:
                            svc = set_events(c_nm, p_typ, t_nm + "_" + d_typ,
                                             a_nm, events, svc)
                    else:
                        svc = set_events(c_nm, p_typ, t_nm, a_nm, events, svc)
        return svc

    def set_descs(self, svc_about):
        """Set descriptions for clients, routers and gateways.
        """
        for about in ("client", "router", "gate"):
            for obj_nm, abt_meta in FI.S[about].items():
                svc_about[about][obj_nm] = abt_meta["desc"]
        return svc_about

    def set_msgs(self):
        """Set named message/record structures.
        """
        svc_msgs = dict()
        for m_nm, m_fields in FI.S["message"].items():
            svc_msgs[m_nm] = {"fields": {}}
            for f_nm, r_values in m_fields.items():
                svc_msgs[m_nm]["fields"][f_nm] = dict()
                if "desc" in r_values.keys():
                    svc_msgs[m_nm]["fields"][f_nm]["desc"] = r_values["desc"]
                if "type" in r_values.keys():
                    svc_msgs[m_nm]["fields"][f_nm]["type"] = r_values["type"]
                if "enum" in r_values.keys():
                    svc_msgs[m_nm]["fields"][f_nm]["enum"] = r_values["enum"]

        return svc_msgs

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

        I'm also thinking that the (duplex) ports assinged to a channel
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
        pypath = path.join(self.APP, FI.D['ADIRS']['PY'], f"{pgm_nm}.py")
        logpath = path.join(FI.D['MEM'], FI.D['APP'],
                            FI.D['ADIRS']['SAV'], FI.D['NSDIRS']['LOG'])
        for c_nm, c_meta in svc.items():
            for p_typ in [pt for pt in c_meta.keys()
                          if pt not in ("host", "desc")]:
                for port in c_meta[p_typ]["port"]:
                    SI.run_nohup_py(pypath, logpath,
                                    f"/{c_nm}/{p_typ}:{port}",
                                    c_meta['host'], port, pgm_nm)
        result, _ = SR.rpt_jobs("/" + pgm_nm)
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

if __name__ == '__main__':
    SI = SaskanInstall()
