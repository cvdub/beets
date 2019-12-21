# -*- coding: utf-8 -*-
# This file is part of beets.
# Copyright 2016, aroquen
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

"""Determine BPM by pressing a key to the rhythm."""

from __future__ import absolute_import, division, print_function

import os
import subprocess
import time

from six.moves import input

from beets import ui
from beets.plugins import BeetsPlugin


def calculate_bpm(song_path, dry_run=False):
    command = ["bpm-tag", "-n", song_path]
    completed_process = subprocess.run(command, capture_output=True)
    command_output = completed_process.stderr.decode("utf-8")
    bpm = float(command_output.split()[-2])
    return round(bpm)


# def bpm(max_strokes):
#     """Returns average BPM (possibly of a playing song)
#     listening to Enter keystrokes.
#     """
#     t0 = None
#     dt = []
#     for i in range(max_strokes):
#         # Press enter to the rhythm...
#         s = input()
#         if s == "":
#             t1 = time.time()
#             # Only start measuring at the second stroke
#             if t0:
#                 dt.append(t1 - t0)
#             t0 = t1
#         else:
#             break

#     # Return average BPM
#     # bpm = (max_strokes-1) / sum(dt) * 60
#     ave = sum([1.0 / dti * 60 for dti in dt]) / len(dt)
#     return ave


class BPMPlugin(BeetsPlugin):
    def __init__(self):
        super(BPMPlugin, self).__init__()
        self.config.add({"max_strokes": 3, "overwrite": False})

    def commands(self):
        cmd = ui.Subcommand("bpm", help="calculate bpm with bpm-tools")
        cmd.func = self.command
        return [cmd]

    def command(self, lib, opts, args):
        should_write = ui.should_write()
        should_overwrite = self.config["overwrite"].get(bool)
        items = lib.items(ui.decargs(args))
        for item in items:
            bpm = calculate_bpm(item.path)
            write = bool(should_write and (item["bpm"] and not should_overwrite))
            self._log.info(f"{item} bpm: {bpm}, updated={write}")
            item["bpm"] = bpm

            if write:
                item.try_write()
            item.store()
