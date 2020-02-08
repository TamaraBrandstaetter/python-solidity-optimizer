##################################################
#   Logic rule 1: Exploit Algebraic Identities   #
#   -------------------------------------------  #
#   Application of the law of De Morgan          #
##################################################

instance_counter = 0
additional_lines = 0


def check_rule(added_lines, file_content, statement):
    global additional_lines
    additional_lines = added_lines
    if statement.condition.type == 'BinaryOperation' \
            and statement.condition.left.type == 'UnaryOperation' and statement.condition.left.operator == '!' \
            and statement.condition.right.type == 'UnaryOperation' and statement.condition.right.operator == '!':
        # found instance of deMorgan
        if statement.condition.operator == '&&' or statement.condition.operator == '||':
            apply_law_of_de_morgan(statement, file_content)
    return additional_lines


def apply_law_of_de_morgan(statement, file_content):
    global instance_counter, additional_lines
    instance_counter += 1
    statement_line = statement.loc['start']['line'] - 1 + additional_lines
    print('### found instance of logic rule 1; line: ' + str(statement_line))

    new_operator = '&&'
    if statement.condition.operator == '&&':
        new_operator = '||'

    left_expression_location = statement.condition.left.subExpression.loc
    left_expression_start = left_expression_location['start']['column']
    left_expression_end = left_expression_location['end']['column'] + 1

    right_expression_location = statement.condition.right.subExpression.loc
    right_expression_start = right_expression_location['start']['column']
    right_expression_end = right_expression_location['end']['column'] + 1

    left_expression = file_content[statement_line][left_expression_start:left_expression_end]
    right_expression = file_content[statement_line][right_expression_start:right_expression_end]

    condition_start = statement.condition.loc['start']['column']
    condition_end = statement.condition.loc['end']['column'] + 1

    if statement.condition.left.subExpression.type == 'Identifier':
        left_expression = statement.condition.left.subExpression.name
    if statement.condition.right.subExpression.type == 'Identifier':
        right_expression = statement.condition.right.subExpression.name
        condition_end = condition_end + len(right_expression) - 1

    replacement = '!(' + left_expression + ' ' + new_operator + ' ' + right_expression + ')'
    statement_to_move = file_content[statement_line][condition_start:condition_end]

    new_line = file_content[statement_line].replace(statement_to_move, replacement)
    file_content.remove(file_content[statement_line])
    file_content.insert(statement_line, new_line)
    comment_line = '// ############ PY_SOLOPT: Found instance of the law of De Morgan. ############\n'
    file_content.insert(statement_line, comment_line)
    additional_lines += 1


def get_instance_counter():
    global instance_counter
    return instance_counter


def get_additional_lines():
    global additional_lines
    return additional_lines
