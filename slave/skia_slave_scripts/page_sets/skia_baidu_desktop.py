# Copyright 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
# pylint: disable=W0401,W0614

from telemetry.page.actions.all_page_actions import *
from telemetry.page import page as page_module
from telemetry.page import page_set as page_set_module


class SkiaBuildbotDesktopPage(page_module.PageWithDefaultRunNavigate):

  def __init__(self, url, page_set):
    super(SkiaBuildbotDesktopPage, self).__init__(url=url, page_set=page_set)
    self.user_agent_type = 'desktop'
    self.archive_data_file = 'data/skia_baidu_desktop.json'
    self.credentials_path = 'data/credentials.json'

  def RunSmoothness(self, action_runner):
    action_runner.RunAction(ScrollAction())

  def RunNavigateSteps(self, action_runner):
    action_runner.RunAction(NavigateAction())
    action_runner.RunAction(WaitAction(
      {
        'seconds': 5
      }))


class SkiaBuildbotPageSet(page_set_module.PageSet):

  """ Pages designed to represent the median, not highly optimized web """

  def __init__(self):
    super(SkiaBuildbotPageSet, self).__init__(
      user_agent_type='desktop',
      credentials_path = 'data/credentials.json',
      archive_data_file='data/skia_baidu_desktop.json')

    urls_list = [
      # Why: #5 (Alexa) most visited worldwide.
      'http://www.baidu.com/s?wd=barack+obama&rsv_bp=0&rsv_spt=3&rsv_sug3=9&rsv_sug=0&rsv_sug4=3824&rsv_sug1=3&inputT=4920',
    ]

    for url in urls_list:
      self.AddPage(SkiaBuildbotDesktopPage(url, self))
