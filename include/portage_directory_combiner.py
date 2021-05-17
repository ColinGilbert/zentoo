#!/usr/bin/env python3

import sys, os 
from .gentoomuch_common import read_file_lines, write_file_lines, read_by_tokens, output_path, config_dir, stage_defines_path, cpu_path, pkgset_path, local_config_basepath, hooks_path, kernel_path, global_config_path, get_cleaned_path

class portage_directory_combiner:
    
    def __init__(self):
        self.todo = dict() # Dict[str, List[str]]
        self.accum = portage_directory()

    def process_stage_defines(self, current_stage):
        current_stage = current_stage.strip()
        # First, we ensure our target output directory is sane.
        self.__prep()
        # Determine whether the stage defines path exists.
        current_stage_defines_path = os.path.join(stage_defines_path, current_stage)
        if not os.path.isdir(current_stage_defines_path):
            sys.exit(msg_prefix + 'Could not find stage definitions directory: ' + current_stage_defines_path)
        # Get CPU part of stage defines.
        cpu_defines_path = os.path.join(current_stage_defines_path, 'cpu')
        if not os.path.isfile(cpu_defines_path):
            sys.exit(msg_prefix + 'Could not find cpu defines file: ' + os.path.join(current_stage_defines_path, 'cpu'))
        cpu_conf = open(os.path.join(current_stage_defines_path, 'cpu')).read().strip()
        # Now we verify CPU-related info.
        local_cpu_path = os.path.join(cpu_path, cpu_conf)
        if not os.path.isdir(local_cpu_path):
            sys.exit(msg_prefix + 'CPU config directory: ' + local_cpu_path + ' does not exist.')
        # Now ingest.
        self.accum.ingest(local_cpu_path)
        # Now, we can pull in the globally-needed parts.
        self.__checkout_common_config()
        # We need to get to the file in which local portage directories are written. 
        flags_defines_path = os.path.join(current_stage_defines_path, 'flags')
        if os.path.isfile(flags_defines_path):
            flags_conf = read_file_lines(flags_defines_path)
        else:
            sys.exit(msg_prefix + 'Stage3 definition flag file: ' + flags_defines_path + ' does not exist.')
        # Now we can loop over all local portages, accumulating them.
        for local in flags_conf:
            combined_path = os.path.join(local_config_basepath, local.strip())
            # Verify directory exists.
            if not os.path.isdir(combined_path):
                sys.exit(msg_prefix + 'Local portage flags config directory ' + combined_path + ' does not exist.')
            # Now ingest.
            print("portage_directory_combiner: Ingesting " + combined_path)
            self.accum.ingest(combined_path)
        # We add info we must use post-munge.
        combined_path = os.path.join(current_stage_defines_path, 'packages')
        if os.path.isfile(combined_path):
            self.todo['packages'] = read_file_lines(combined_path)
        combined_path = os.path.join(current_stage_defines_path, 'profiles')
        if os.path.isfile(combined_path):
            self.todo['profiles'] = read_file_lines(combined_path)
        combined_path = os.path.join(current_stage_defines_path, 'hooks')
        if os.path.isfile(combined_path):
            self.todo['hooks'] = read_file_lines(combined_path)
        # Now we write-out the files themselves
        self.accum.writeout()

    def __prep(self):
        if debug:
            print('Prepping munged portagedir environment.')
        if not os.path.isdir(output_path):
            os.mkdir(output_path)
        code = os.system('rm -rf ' + os.path.join(output_path, '*'))
        if not code == 0:
            sys.exit('portage_directory_combiner - could not clean output dir')

    def __checkout_common_config(self):
        # Verify existence of global config directory.
        if not os.path.isdir(global_config_path):
            sys.exit('Global Portage  config directory at ' + global_config_path + ' does not exist.')
        # Ingest that thing.
        self.accum.ingest(global_config_path)
        # Here, we deal with the (package) sets and patches.
        rsync_cmd = 'rsync -aHVXq'
        sync_sets_str = rsync_cmd + ' ' + os.path.join(pkgset_path, '*') + ' '  + sets_output_path
        sync_patches_str = rsync_cmd + ' ' + os.path.join(patches_path, '*') + ' ' + patches_output_path
        # A helper to print error messages without copying code.
        def print_rsync_error(tag):
            sys.exit("stage_combiner.checkout_common_config() - Could not rsync " + tag + "with error code: " + code)
        # We now add package sets. These are universal.
        code = os.system(sync_sets_str)
        if not code == 0:
            print_rsync_error('sets')
        code = os.system(sync_patches_str)
        if not code == 0:
            print_rsync_error('patches')