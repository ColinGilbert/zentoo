#!/usr/bin/env python3

import re


def get_dockerized_profile_name(profile):
  return re.sub(re.escape('+'), '-', profile) # Found that one out when working with musl+selinux...
