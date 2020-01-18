###################################################
#   Loop rule 3: Transfer-Driven Loop Unrolling   #
#   -------------------------------------------   #
#   Removing trivial assignments (aliases)        #
#   within a loop and replacing them with the     #
#   values themselves reduces the required space. #
###################################################

import pprint

additional_lines = 0
instance_counter = 0


def check_rule(added_lines, file_content):
    global additional_lines
    additional_lines = added_lines
    return additional_lines


def get_instance_counter():
    global instance_counter
    return instance_counter


def get_additional_lines():
    global additional_lines
    return additional_lines
