###################################################
#   Loop rule 3: Loop Unrolling                   #
#   -------------------------------------------   #
#   Removing trivial assignments (aliases)        #
#   within a loop and replacing them with the     #
#   values themselves reduces the required space. #
###################################################

additional_lines = 0
instance_counter = 0


def check_rule(added_lines, file_content, loop_statement):
    global additional_lines
    additional_lines = added_lines

    if (loop_statement.conditionExpression and loop_statement.conditionExpression.type == 'BinaryOperation'
            and (loop_statement.conditionExpression.operator != '&&'
                 or loop_statement.conditionExpression.operator != '||')):
        # check initexpression
        if loop_statement.initExpression and loop_statement.initExpression.type == 'VariableDeclarationStatement' \
                and loop_statement.initExpression.variables:
            initial_value = 0
            exit_value = 0
            loop_var_name = loop_statement.initExpression.variables[0].name
            if loop_statement.initExpression.initialValue is not None \
                    and loop_statement.initExpression.initialValue.type == 'NumberLiteral':
                initial_value = int(loop_statement.initExpression.initialValue.number)

                # check loopExpression
                if loop_statement.loopExpression \
                        and loop_statement.loopExpression.type == 'ExpressionStatement' \
                        and loop_statement.loopExpression.expression is not None \
                        and loop_statement.loopExpression.expression.type == 'UnaryOperation' \
                        and (loop_statement.loopExpression.expression.operator == '++'
                             or loop_statement.loopExpression.expression.operator == '--'):
                    # check conditionExpression
                    if loop_statement.conditionExpression \
                            and loop_statement.conditionExpression.type == 'BinaryOperation' \
                            and loop_statement.conditionExpression.right.type == 'NumberLiteral' \
                            and loop_statement.conditionExpression.left.type == 'Identifier' \
                            and loop_statement.conditionExpression.left.name == loop_var_name:
                        exit_value = int(loop_statement.conditionExpression.right.number)
                        lt = exit_value - initial_value
                        gt = initial_value - exit_value
                        if (loop_statement.conditionExpression.operator == '<' and 0 < lt <= 8) \
                                or (loop_statement.conditionExpression.operator == '<=' and 0 < lt < 8) \
                                or (loop_statement.conditionExpression.operator == '>' and 0 < gt <= 8) \
                                or (loop_statement.conditionExpression.operator == '>=' and 0 < gt < 8):
                            unroll_loop(file_content, loop_statement, initial_value,
                                        loop_statement.conditionExpression.operator, exit_value, loop_var_name)
    return additional_lines


def unroll_loop(file_content, loop_statement, start_value, condition_operator, exit_value, var_name):
    global additional_lines, instance_counter

    loop_statements = {}
    if loop_statement.body and loop_statement.body.type == 'Block':
        loop_statements = loop_statement.body.statements
    else:
        return

    loop_location = loop_statement.loc
    loop_line = loop_location['start']['line'] - 1 + additional_lines
    loop_end = loop_location['end']['line'] + additional_lines
    tabs_to_insert = ' ' * loop_location['start']['column']

    range_value = []
    if condition_operator == '<':
        range_value = range(exit_value - 1, start_value - 1, -1)
    elif condition_operator == '<=':
        range_value = range(exit_value, start_value - 1, -1)
    elif condition_operator == '>':
        range_value = range(exit_value, start_value)
    elif condition_operator == '>=':
        range_value = range(exit_value, start_value + 1)

    file_changed = 0
    for i in range_value:
        file_changed += add_loop_content(file_content, loop_line, tabs_to_insert, loop_statements, var_name, i)

    # remove whole loop from file content
    if file_changed > 0:
        remove_counter = 0
        for i in range(loop_line, loop_end):
            del file_content[loop_line + file_changed]
            remove_counter += 1
        additional_lines -= remove_counter
        comment_line = '// ### PY_SOLOPT ### Found a rule violation of Loop Rule 3. Loop was automatically unrolled.\n'
        file_content.insert(loop_line, tabs_to_insert + comment_line)
        additional_lines += 1
    else:
        comment_line1 = '// ### PY_SOLOPT ### Found a POSSIBLE rule violation of Loop Rule 3 Unrolling loop.\n'
        comment_line2 = '// ### PY_SOLOPT ### Try to unroll the loop to improve the gas consumption.\n'
        file_content.insert(loop_line, tabs_to_insert + comment_line2)
        file_content.insert(loop_line, tabs_to_insert + comment_line1)
        additional_lines += 2

    print('### found instance of loop rule 3; line: ' + str(loop_statement.loc['start']['line']))
    instance_counter += 1


def add_loop_content(file_content, loop_line, tabs, statements, variable_name, variable_value):
    global additional_lines
    added_lines = 0
    for statement in statements:
        if statement.type != 'ExpressionStatement':
            return 0
    for statement in statements:
        statement_line = file_content[statement.loc['start']['line'] - 1 + additional_lines]
        new_line = check_statement(statement.expression, statement_line, variable_name, variable_value)
        file_content.insert(loop_line, tabs + new_line.lstrip(' '))
        additional_lines += 1
        added_lines += 1
    return added_lines


def check_statement(expression, line, var_name, var_value):
    if expression.type == 'BinaryOperation':
        return check_binary_operation(expression, line, var_name, var_value)
    elif expression.type == 'FunctionCall':
        return check_function_call(expression, line, var_name, var_value)
    elif expression.type == 'Identifier':
        return check_identifier(expression, line, var_name, var_value)
    elif expression.type == 'IndexAccess':
        return check_index_access(expression, line, var_name, var_value)
    elif expression.type == 'TupleExpression':
        return check_tuple_expression(expression, line, var_name, var_value)
    elif expression.type == 'MemberAccess':
        return check_statement(expression.expression, line, var_name, var_value)
    return line


def check_tuple_expression(expression, line, var_name, var_value):
    new_line = line
    if expression.components:
        for component in expression.components:
            new_line = check_statement(component, new_line, var_name, var_value)
    return new_line


def check_function_call(expression, line, var_name, var_value):
    new_line = line
    if expression.arguments:
        for argument in expression.arguments:
            new_line = check_statement(argument, new_line, var_name, var_value)
    return new_line


def check_binary_operation(expression, line, var_name, var_value):
    left_expr = expression.left
    right_expr = expression.right
    new_line = check_statement(left_expr, line, var_name, var_value)
    new_line = check_statement(right_expr, new_line, var_name, var_value)
    return new_line


def check_index_access(expression, line, var_name, var_value):
    return check_statement(expression.index, line, var_name, var_value)


def check_identifier(expression, line, var_name, var_value):
    if expression.name == var_name:
        if len(var_name) == 1:
            return line[:expression.loc['start']['column']] + str(var_value) + line[expression.loc['end']['column'] + 1:]
        else:
            if str(line[:expression.loc['start']['column'] + 1]).endswith(var_name):
                return line[:expression.loc['start']['column'] + 1 - len(var_name)] + str(var_value) + line[expression.loc['end']['column'] + 1:]
            elif str(line[expression.loc['end']['column']:]).startswith(var_name):
                return line[:expression.loc['start']['column']] + str(var_value) + line[expression.loc['end']['column'] + len(var_name):]
    return line


def get_instance_counter():
    global instance_counter
    return instance_counter


def get_additional_lines():
    global additional_lines
    return additional_lines
