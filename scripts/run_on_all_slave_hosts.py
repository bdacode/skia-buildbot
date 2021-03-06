#!/usr/bin/env python
# Copyright (c) 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


"""Run a command on all build slave host machines listed in slave_hosts_cfg."""


import run_cmd


if '__main__' == __name__:
  options = run_cmd.parse_args()
  results = run_cmd.run_on_all_slave_hosts(options.cmd)
  results.print_results(pretty=options.pretty)
