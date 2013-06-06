# Copyright (c) 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


""" Utilities for dealing with builder names. This module obtains its attributes
dynamically from builder_name_schema.json. """


import json
import os


def _LoadSchema():
  """ Load the builder naming schema from the JSON file. """

  def _UnicodeToStr(obj):
    """ Convert all unicode strings in obj to Python strings. """
    if isinstance(obj, unicode):
      return str(obj)
    elif isinstance(obj, dict):
      return dict(map(_UnicodeToStr, obj.iteritems()))
    elif isinstance(obj, list):
      return list(map(_UnicodeToStr, obj))
    elif isinstance(obj, tuple):
      return tuple(map(_UnicodeToStr, obj))
    else:
      return obj

  builder_name_json_filename = os.path.join(
      os.path.dirname(__file__), 'builder_name_schema.json')
  builder_name_schema_json = json.load(open(builder_name_json_filename))
  for k, v in builder_name_schema_json.iteritems():
    globals()[str(k).upper()] = _UnicodeToStr(v)

  # Roles specify different types of builders.
  builder_role_template = 'BUILDER_ROLE_%s'

  #pylint: disable=E0602
  for role in BUILDER_NAME_SCHEMA.keys():
    globals()[builder_role_template % role.upper()] = role

_LoadSchema()


def MakeBuilderName(role, extra_config=None, is_trybot=False, **kwargs):
  #pylint: disable=E0602
  schema = BUILDER_NAME_SCHEMA.get(role)
  if not schema:
    raise ValueError('%s is not a recognized role.' % role)
  for k, v in kwargs.iteritems():
    if BUILDER_NAME_SEP in v:
      raise ValueError('%s not allowed in %s.' % (BUILDER_NAME_SEP, v))
    if not k in schema:
      raise ValueError('Schema does not contain "%s": %s' %(k, schema))
  if extra_config and BUILDER_NAME_SEP in extra_config:
    raise ValueError('%s not allowed in %s.' % (BUILDER_NAME_SEP,
                                                extra_config))
  name_parts = [role]
  name_parts.extend([kwargs[attribute] for attribute in schema])
  if extra_config:
    name_parts.append(extra_config)
  if is_trybot:
    name_parts.append(TRYBOT_NAME_SUFFIX)
  return BUILDER_NAME_SEP.join(name_parts)


def IsTrybot(builder_name):
  #pylint: disable=E0602
  return builder_name.endswith(TRYBOT_NAME_SUFFIX)