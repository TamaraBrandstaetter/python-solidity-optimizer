#################################################
#   Loop rule 4: Unconditional Branch Removing  #
#   ------------------------------------------  #
#   Using a do-while loop instead of a while-   #
#   or for-loop removes a conditional jump      #
#   operation at the beginning of the loop.     #
#################################################

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
