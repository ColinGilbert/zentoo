#!/usr/bin/env python3

import re

# Stuff all scripts here should use

output_path                 = './work/portage/'
config_dir                  = './config/'
stage_defines_path          = config_dir + 'stage.defines/'
cpu_path                    = config_dir + 'cpu.defines/'
pkgset_path                 = config_dir + 'package.sets/'
patches_path                = config_dir + 'patches/'
local_config_basepath       = config_dir + 'portage.locals/'
hooks_path                  = config_dir + 'build.hooks/'
kernel_path                 = config_dir + 'kernel.defines/'
global_config_path          = './include/portage.global/'
arch_config_path            = config_dir + 'arch'

debug = True

sets_output_path = './work/portage/sets'
patches_output_path = './work/portage/patches'

# TODO: Move these convenience functions
def read_file_lines(filename):
    f = open(filename)
    lines = f.readlines()
    return lines

def write_file_lines(filename, lines):
    f = open(filename, 'w')
    f.writelines(lines)
    f.close()

# https://stackoverflow.com/questions/16402525/python-read-whitespace-separated-strings-from-file-similar-to-readline
def read_by_tokens(obj):
    for line in obj:
        for token in line.split():
            yield token

# TODO: Write a test or two
def get_cleaned_path(dirpath, local_config_path):
    results = dirpath
    results = re.sub(re.escape(local_config_path)           , '', results)
    results = re.sub(re.escape(output_path)                 , '', results)
    results = re.sub(re.escape(global_config_path)          , '', results)
    results = re.sub(re.escape(local_config_basepath)       , '', results)
    results = re.sub(re.escape(cpu_path)                    , '', results)
    results = re.sub('^/'                                   , '', results)
    return results
