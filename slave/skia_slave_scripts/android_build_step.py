# Copyright (c) 2012 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

""" Subclass for all slave-side Android build steps. """

from build_step import BuildStep

class AndroidBuildStep(BuildStep):
  def __init__(self, args, attempts=1):
    self._device = args['device']
    super(AndroidBuildStep, self).__init__(args, attempts)