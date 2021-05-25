#!/usr/bin/env python3

import os, sys, re
from include.gentoomuch_common import read_file_lines, write_file_lines, config_path, active_image_tag

builder_str = 'builder'
packer_str = 'packer'
updater_str = 'updater'

# This uses the current state of the work/portage directory and automatically creates a composefile that'll properly include each file. This avoids much handcruft.
def create_composefile( output_path):
    lines = ['# Do not make changes to this file, as they will be overriden upon the next build.\n' , 'services:\n']
    lines.extend(__output_config(builder_str))
    lines.extend(__output_config(packer_str))
    lines.extend(__output_config(updater_str))
    include_prefix = 'include/docker-compose/docker-compose.'
    lines.append('networks:\n')
    lines.append('  backend:\n')
    lines.append('    driver: overlay\n')
    lines.append('volumes:\n')
    lines.append('  distfiles:\n')
    lines.append('    driver: local\n')
    lines.append('  ebuilds:\n')
    lines.append('    driver: local\n')
    lines.append('  binpkgs:\n')
    lines.append('    driver: local\n')
    lines.append('  kernels:\n')
    lines.append('    driver: local\n')
    write_file_lines(os.path.join(output_path, 'docker-compose.yml'), lines)

def __output_config(container_type_str):
    if not container_type_str == builder_str and not container_type_str == packer_str and not container_type_str == updater_str:
        sys.exit('Gentoomuch.create-composefile: Invalid container type argument \"' + updater_str  +  '\"')
    is_builder  = bool(container_type_str == builder_str)
    is_packer   = bool(container_type_str == packer_str)
    is_updater  = bool(container_type_str == updater_str)
    # Our results will be a list of strings.
    results = [] 
    # First, we define whether this'll be a builder or a packer.
    results.append('  gentoomuch-' + container_type_str + ':\n')
    # We append the universal parts.
    results.append('    # The following line is a cool trick that fools the docker program into using a locally-tagged image as if it came from a proper repository.\n')
    results.append('    image: ' + active_image_tag + ':latest\n')
    results.append('    networks:\n')
    results.append('    - backend\n')
    results.append('    volumes:\n')
    results.append('    - /dev:/dev\n')
    results.append('    - /proc:/proc\n')
    results.append('    - /sys:/sys:ro\n')
    # These are the parts that have different permissions between the two types of containers.
    binpkg_str          = '    - binpkgs:/var/cache/binpkgs'
    distfiles_str       = '    - distfiles:/var/cache/distfiles'
    ebuilds_str         = '    - ebuilds:/var/db/repos/gentoo'
    kernels_str         = '    - kernels:/mnt/kernels'
    squashed_output_str = '    - ./squashed/blob:/mnt/squashed-portage'
    squashed_mount_str  = '    - ./squashed/mountpoint:/mnt/squashed-portage'
    stages_mount_str    = '    - ./stages:/mnt/stages'
    # Here we actually write these differential parts into our list.
    if is_packer:
        results.append(binpkg_str + ':ro\n')
        results.append(distfiles_str + ':ro\n')
        results.append(ebuilds_str + ':ro\n')
        results.append(kernels_str + ':ro\n')
        results.append(squashed_mount_str + ':ro\n')
        results.append(stages_mount_str + '\n')
    if is_builder:
        results.append(binpkg_str + '\n')
        results.append(distfiles_str +'\n')
        results.append(ebuilds_str + '\n')
        results.append(kernels_str + '\n')
        results.append(squashed_mount_str + ':ro\n')
        results.append(stages_mount_str + ':ro\n')
    if is_updater:
        results.append(binpkg_str + '\n')
        results.append(distfiles_str +'\n')
        results.append(ebuilds_str + '\n')
        results.append(kernels_str + '\n')
        results.append(squashed_output_str + '\n')
        results.append(stages_mount_str + ':ro\n')
    # Here we loop over the all the files in the config/portage directory and add them.
    portage_tgt = '/etc/portage/'
    for (dirpath, directories, files) in os.walk('work/portage'):
        for f in files:
            if not f[0] == '.' and not f == 'README.md':
                #dir_str = re.sub(re.escape('./work'), '', dirpath) 
                #results.append('    - ./' + os.path.join(dir_str, f) + ':' + re.sub(re.escape('/work/portage'), '', os.path.join(portage_tgt, dir_str, f)) + ':ro\n')
                results.append('    - ./' + os.path.join(os.path.relpath(dirpath, 'work'), f) + ':' + os.path.join(portage_tgt, f) + ':ro\n')
    if is_packer:
        results.append('    cap_add:\n')
        results.append('    - CAP_SYS_ADMIN\n')
    # Finally, we return the list of string.
    return results