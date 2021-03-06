#################################################
#   Loop rule 2: Combining Tests                #
#   ------------------------------------------  #
#   Reduces the number of evaluated conditions  #
#   within a loop.                              #
#################################################

additional_lines = 0
instance_counter = 0


def check_rule(added_lines, file_content, loop_statement):
    global additional_lines, instance_counter
    additional_lines = added_lines
    if loop_statement.type == 'WhileStatement' or loop_statement.type == 'DoWhileStatement':
        if (loop_statement.condition and loop_statement.condition.type == 'BinaryOperation'
                and (loop_statement.condition.operator == '&&' or loop_statement.condition.operator == '||')):
            add_comment_above(file_content, loop_statement.loc)
            print('### found instance of loop rule 2; line: '
                  + str(loop_statement.loc['start']['line'] + additional_lines))
            instance_counter += 1
    elif loop_statement.type == 'ForStatement':
        if (loop_statement.conditionExpression and loop_statement.conditionExpression.type == 'BinaryOperation'
                and (loop_statement.conditionExpression.operator == '&&'
                     or loop_statement.conditionExpression.operator == '||')):
            add_comment_above(file_content, loop_statement.loc)
            print('### found instance of loop rule 2; line: '
                  + str(loop_statement.loc['start']['line'] + additional_lines))
            instance_counter += 1
    return additional_lines


def add_comment_above(file_content, loop_location):
    global additional_lines
    function_line = loop_location['start']['line'] - 1 + additional_lines
    tabs_to_insert = ' ' * loop_location['start']['column']
    new_line = '// ### PY_SOLOPT ### Found a POSSIBLE rule violation of Loop Rule 2.\n'
    new_line2 = '// ### PY_SOLOPT ### Try to combine the tests in the loop ' \
                'in order to contain (in the best case) only one condition.\n'
    file_content.insert(function_line, tabs_to_insert + new_line2)
    file_content.insert(function_line, tabs_to_insert + new_line)
    additional_lines += 2


def get_instance_counter():
    global instance_counter
    return instance_counter


def get_additional_lines():
    global additional_lines
    return additional_lines
