
def check_loop_rule_1(file_content, loop_statement):
    loop_location = loop_statement.loc
    loop_expressions = loop_statement.initExpression
    loop_body = loop_statement.body

    for variable in loop_expressions.variables:
        for loop_statement in loop_body.statements:
            if not statement_contains_identifier(loop_statement, variable.name):
                pprint.pprint("############ found instance of rule #2 #############")

                tabs_to_insert = '\t' * loop_location['start']['column']
                loop_line = loop_location['start']['line'] - 1
                line_to_move = loop_statement.loc['start']['line'] - 1
                statement_start = loop_statement.loc['start']['column']
                statement_end = loop_statement.loc['end']['column']

                pprint.pprint(loop_statement.loc)

                statement_to_insert = tabs_to_insert + content[line_to_move][statement_start:statement_end + 1]
                pprint.pprint(statement_to_insert)
                content.remove(content[line_to_move])
                content.insert(loop_line, statement_to_insert + "\n")
            elif not assignment_right_side_contains_identifier(loop_statement, variable.name):
                pprint.pprint("############ found instance of rule #2 #############")
    return True


def move_statement_up(loop_statement, variable_name):
    if loop_statement.type == 'VariableDeclarationStatement':
        initial_value = loop_statement.initialValue
    else:
        return True
    # as identifier
    if initial_value.type == 'Identifier':
        return identifier_is_loop_variable(initial_value, variable_name)
    # as part of an operation
    if initial_value.type == 'BinaryOperation':
        return binary_operation_contains_identifier(initial_value, variable_name)


def identifier_is_loop_variable(initial_value, variable_name):
    return initial_value.name == variable_name


def binary_operation_contains_identifier(initial_value, variable_name):
    left = initial_value.left
    if left.type == 'BinaryOperation':
        return binary_operation_contains_identifier(left, variable_name)
    elif left.type == 'Identifier':
        return identifier_is_loop_variable(left, variable_name)
    right = initial_value.right
    if right.type == 'BinaryOperation':
        return binary_operation_contains_identifier(right, variable_name)
    elif right.type == 'Identifier':
        return identifier_is_loop_variable(right, variable_name)
    return False
