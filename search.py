import navegador5.shell_cmd as nvsh

import collections
import copy
import re
import urllib
import os
import json
import sys
import time


from xdict.jprint import  pobj
from xdict.jprint import  print_j_str
from xdict import cmdline
from xdict.jprint import pdir


def ls_l(keywords,dirname):
    shell_cmds = {}
    shell_cmds[1] = 'ls -l ' + dirname
    shell_cmds[2] = 'egrep ' + keywords
    shell_cmds[3] = "awk {'print $9'}"
    genuses = nvsh.pipe_shell_cmds(shell_cmds)[0].decode('utf-8').split('\n')
    del genuses[-1]
    shell_cmds = {}
    shell_cmds[1] = 'ls -l ' + dirname
    shell_cmds[2] = 'egrep ' + keywords
    shell_cmds[3] = "awk {'print $10'}"
    species = nvsh.pipe_shell_cmds(shell_cmds)[0].decode('utf-8').split('\n')
    del species[-1]
    results = []
    for i in range(0,genuses.__len__()):
        result = dirname + '/' + genuses[i] + ' ' + species[i]
        results.append(result)
    return(results)


keywords = sys.argv[2]



img_paths = ls_l(keywords,'Images')
shell_cmds = {}
shell_cmds[1] = 'rm -r SEARCHED'
shell_cmds[2] = 'mkdir SEARCHED'
nvsh.pipe_shell_cmds(shell_cmds)
for each in img_paths:
    name = each.split('_')[-1]
    shell_cmds = {}
    shell_cmds[1] = 'cp ' + '"'+each+'"' + ' ' + 'SEARCHED/' + name
    nvsh.pipe_shell_cmds(shell_cmds)

