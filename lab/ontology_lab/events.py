#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module provides Functions which handle events triggered by forms
or other sources of events.  For example, when a user clicks on a
Submit button, what logic needs to occur, or when a GET event is
triggered, what template is rendered.  As a program gets more complex
it may be useful to separate submit (POST) event logic into a separate module
from the logic to render GET events.
"""

# python modules
import logging
import subprocess32 as sh
# An event may include Views used to display some stuff:
from flask import render_template
# Local modules
import sys
sys.path.append('.')
from main import utils

# FUNCTIONS
# =========================
# Compute Universal Pecentages
# ==========================================
def submit_compute_pcts(msgs, apptxts, gxsteps, univ):
    """
    Handle POST result for /bang
    Run computations for computing percentages of super-clusters vs.
    regular galactic clusters and how much of the universe they occupy.

    Args:
        msgs:       Message handler object
        apptxts:    Application texts dict
        gxsteps:    Galaxy building process steps
        univ:       Universe object
    """
    logging.info('Computing universal percentages...')

    step = gxsteps.get_step()
    if step["num"] == 0:
        logging.info('Starting step process..')
    elif step["num"] == 1:
        univ.set_supergx_sector_pct(apptxts, gxsteps, "random")
    elif step["num"] == 2:
        univ.set_reggx_sector_pct(apptxts, gxsteps, "random")
    elif step["num"] == 3:
        univ.set_empty_univ_pct(apptxts, gxsteps)
    elif step["num"] == 4:
        univ.set_super_gx_pct(apptxts, gxsteps, "random")
    elif step["num"] == 5:
        univ.set_reggx_pct(apptxts, gxsteps)
    elif step["num"] == 6:
        univ.set_supergx_cnt(apptxts, gxsteps)
    elif step["num"] == 7:
        univ.set_reggx_cnt(apptxts, gxsteps)

    if step["num"] == step["max"]:
        msg = "<" + str(utils.dt_dYmdHZ_Now()) + ">" + \
              apptxts["set01Name"] + ": " + apptxts["done"]
        logging.info(msg)
    gxsteps.next_rule()

# def render_compute_pcts(form, apptxts, gxsteps):
def render_compute_pcts(form, apptxts):
    """
    Handle GET result for /bang

    Args:
        form:       Flask form for submitting the computation
        apptxts:    Application texts dict

    Returns:
        Rendered template for bang.html
    """
    # return render_template('bang.html', form=form, txts=apptxts,
    #                         steps=gxsteps)
    return render_template('bang.html', form=form, txts=apptxts)


# Shut Down the app
# ==========================================
def submit_shut_down(pids):
    """
    Handle a Shut Down POST event from index/index.html

    Args:
        pids:  List of process IDs
    """
    # Close queue connections
    # logging.info('Closing queue connections...')
    # Recycle the rabbitmq server
    # This will make sure everything gets cleared and refreshed
    # logging.info('Recycling rabbitmq application...')
    # MQ.Refresh()
    logging.info('Killing the web app processes...')
    # Kill the bowrun shell
    sess = sh.Popen(["kill", pids["bowrunweb.sh"]],
                    stdin=sh.PIPE, stdout=sh.PIPE)
    sess_output, sess_err = sess.communicate()
    logging.info(str(sess_output).join(str(sess_err)))
    # Kill the web app
    sess = sh.Popen(["kill", pids["app/bow.py"]],
                    stdin=sh.PIPE, stdout=sh.PIPE)
    sess_output, sess_err = sess.communicate()
    logging.info(str(sess_output).join(str(sess_err)))
