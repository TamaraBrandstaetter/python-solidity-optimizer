#################################################
#   Loop rule 6: Loop Fusion                    #
#   ------------------------------------------  #
#   Combining loops across the same collections #
#   to one can save computation and space.      #
#################################################

import re

additional_lines = 0
instance_counter = 0


def check_rule(added_lines, file_content, first_loop, second_loop):
    global additional_lines, instance_counter
    additional_lines = added_lines
    if first_loop.initExpression and first_loop.initExpression.type == 'VariableDeclarationStatement' \
            and second_loop.initExpression and second_loop.initExpression.type == 'VariableDeclarationStatement':
        # naive way: check if both lines as strings are the same:
        first_loop_location = first_loop.loc['start']['line'] - 1 + additional_lines
        second_loop_location = second_loop.loc['start']['line'] - 1 + additional_lines

        if file_content[first_loop_location] == file_content[second_loop_location]:
            # todo: check whether loop var is reset
            first_loop_end_location = first_loop.loc['end']['line'] - 1 + additional_lines
            first_loop_end = file_content[first_loop_end_location]
            del file_content[second_loop_location]
            if bool(re.match('^[\t\n {]+$', file_content[second_loop_location])):
                del file_content[second_loop_location]
                additional_lines -= 1
            if bool(re.match('^[\t\n }]+$', first_loop_end)):
                del file_content[first_loop_end_location]
                additional_lines -= 1
            comment_line = '// ### PY_SOLOPT ### Found a rule violation of Loop Rule 6 - Loop fusion.\n'
            tabs_to_insert = ' ' * first_loop.loc['start']['column']
            print('####### found instance of loop rule 6')
            print('####### Line:' + str(first_loop_location))
            file_content.insert(first_loop_location, tabs_to_insert + comment_line)
            instance_counter += 1
    return additional_lines


def get_instance_counter():
    global instance_counter
    return instance_counter


def get_additional_lines():
    global additional_lines
    return additional_lines
