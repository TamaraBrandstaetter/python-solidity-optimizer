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


def check_rule(added_lines, file_content, loop_statement):
    global additional_lines
    additional_lines = added_lines

    if loop_statement.initExpression and loop_statement.initExpression.type == 'VariableDeclarationStatement' \
            and loop_statement.initExpression.variables:
        loop_var_name = loop_statement.initExpression.variables[0].name
        if loop_statement.body and loop_statement.body.type == 'Block':
            replace_trivial_assignment(loop_statement.body.statements, loop_var_name, file_content)
    return additional_lines


def replace_trivial_assignment(loop_statements, loop_var_name, file_content):
    for statement in loop_statements:
        if statement.type == 'VariableDeclarationStatement' \
                and statement.variables \
                and statement.initialValue is not None \
                and statement.initialValue.type == 'Identifier' \
                and statement.initialValue.name == loop_var_name:
            var_name = statement.variables[0].name
            if not var_is_reset(loop_statements, statement, var_name):
                pprint.pprint("Found occurence of Loop Rule 4")
                pprint.pprint("Line: " + str(statement.loc['start']['line']))
                # todo: replace all occurrences of var_name with loop_var_name
                # replace_alias(loop_statements, statement, var_name, loop_var_name, file_content)
                tabs_to_insert = ' ' * statement.loc['start']['column']
                comment_line = '// ### PY_SOLOPT ### Found a rule violation of Loop Rule 4:\n'
                comment_line2 = '// TODO: Replace alias \'' + var_name + '\' by the variable \'' + loop_var_name + \
                                '\' and remove the declaration in order to save gas.\n'
                file_content.insert(statement.loc['start']['line'] - 1 + additional_lines,
                                    tabs_to_insert + comment_line2)
                file_content.insert(statement.loc['start']['line'] - 1 + additional_lines,
                                    tabs_to_insert + comment_line)


# def replace_alias(loop_statements, var_statement, var_alias, var_name, file_content):
#     global additional_lines
#     hit = False
#     for statement in loop_statements:
#         if not hit:
#             if statement == var_statement:
#                 hit = True
#             else:
#                 continue
#         else:
#             remove var_alias from statements, remove var_statement line
# statement_line = file_content[statement.loc['start']['line'] - 1 + additional_lines]
# new_line = check_statement(statement, statement_line, var_alias, var_name)
# if statement_line != new_line:
#     file_content.insert(statement.loc['start']['line'], new_line)
#     del file_content[statement.loc['start']['line']]
# added_lines += 1
# tabs_to_insert = ' ' * var_statement.loc['start']['column']
# comment_line = '// ### PY_SOLOPT ### Found a rule violation of Loop Rule 4. Replace alias \'' \
#                + var_alias + '\' by the variable \'' + var_name + '\' in order to save gas.\n'
# file_content.insert(var_statement.loc['start']['line'] - 1 + additional_lines, tabs_to_insert + comment_line)
# del file_content[var_statement.loc['start']['line'] + additional_lines]


def var_is_reset(loop_statements, var_statement, var_name):
    hit = False
    for statement in loop_statements:
        if not hit:
            if statement == var_statement:
                hit = True
            else:
                continue
        else:
            if statement_contains_var(statement, var_name):
                return True
    return False


def statement_contains_var(statement, var_name):
    if isinstance(statement, str):
        # would result in an AttributeError when there is no statement type. example: 'throw;' or 'break;'
        return False
    if statement.type == 'IfStatement':
        if statement.TrueBody:
            if statement.FalseBody is not None:
                return statement_contains_var(statement.TrueBody, var_name) or statement_contains_var(
                    statement.FalseBody, var_name)
            else:
                return statement_contains_var(statement.TrueBody, var_name)
    elif statement.type == 'Block':
        for block_statement in statement.statements:
            if statement_contains_var(block_statement, var_name):
                return True
    elif statement.type == 'ForStatement' or statement.type == 'WhileStatement' or statement.type == 'DoWhileStatement':
        if statement.body is not None:
            return statement_contains_var(statement.body, var_name)
    elif statement.type == 'ExpressionStatement':
        return expression_contains_var(statement.expression, var_name)
    return False


def expression_contains_var(expression, var_name):
    if expression.type == 'BinaryOperation' \
            and (expression.operator == '=' or expression.operator == '+=' or expression.operator == '-='):
        left_expr = expression.left
        return expression_contains_var(left_expr, var_name)
    elif expression.type == 'UnaryOperation':
        return expression_contains_var(expression.subExpression, var_name)
    elif expression.type == 'Identifier' and expression.name == var_name:
        return True
    return False


# def check_statement(statement, line, var_name, var_value):
#     if statement.type == 'IfStatement':
#         if statement.TrueBody:
#             if statement.FalseBody is not None:
#                 new_line = check_statement(statement.TrueBody, line, var_name, var_value)
#                 return check_statement(statement.FalseBody, new_line, var_name, var_value)
#             else:
#                 return check_statement(statement.TrueBody, line, var_name, var_value)
#     elif statement.type == 'Block':
#         new_line = ''
#         for block_statement in statement.statements:
#             new_line += check_statement(block_statement, line, var_name, var_value)
#         return new_line
#     elif statement.type == 'ForStatement':
#         if statement.body is not None:
#             return check_statement(statement.body, line, var_name, var_value)
#     elif statement.type == 'ExpressionStatement':
#         return check_expression(statement.expression, line, var_name, var_value)
#     return False
#
#
# def check_expression(expression, line, var_name, var_value):
#     if expression.type == 'BinaryOperation':
#         return check_binary_operation(expression, line, var_name, var_value)
#     elif expression.type == 'FunctionCall':
#         return check_function_call(expression, line, var_name, var_value)
#     elif expression.type == 'Identifier':
#         return check_identifier(expression, line, var_name, var_value)
#     elif expression.type == 'IndexAccess':
#         return check_index_access(expression, line, var_name, var_value)
#     elif expression.type == 'TupleExpression':
#         return check_tuple_expression(expression, line, var_name, var_value)
#     elif expression.type == 'MemberAccess':
#         return check_expression(expression.expression, line, var_name, var_value)
#     return line
#
#
# def check_tuple_expression(expression, line, var_name, var_value):
#     new_line = line
#     if expression.components:
#         for component in expression.components:
#             new_line = check_expression(component, new_line, var_name, var_value)
#     return new_line
#
#
# def check_function_call(expression, line, var_name, var_value):
#     new_line = line
#     if expression.arguments:
#         for argument in expression.arguments:
#             new_line = check_expression(argument, new_line, var_name, var_value)
#     return new_line
#
#
# def check_binary_operation(expression, line, var_name, var_value):
#     left_expr = expression.left
#     right_expr = expression.right
#     new_line = check_expression(left_expr, line, var_name, var_value)
#     new_line = check_expression(right_expr, new_line, var_name, var_value)
#     return new_line
#
#
# def check_index_access(expression, line, var_name, var_value):
#     return check_expression(expression.index, line, var_name, var_value)
#
#
# def check_identifier(expression, line, var_name, var_value):
#     if expression.name == var_name:
#         if len(var_name) == 1:
#             return line[:expression.loc['start']['column']] + str(var_value) + line[expression.loc['end']['column'] + 1:]
#         else:
#             if str(line[:expression.loc['start']['column'] + 1]).endswith(var_name):
#                 return line[:expression.loc['start']['column'] + 1 - len(var_name)] + str(var_value) + line[expression.loc['end']['column'] + 1:]
#             elif str(line[expression.loc['end']['column']:]).startswith(var_name):
#                 return line[:expression.loc['start']['column']] + str(var_value) + line[expression.loc['end']['column'] + len(var_name):]
#     return line


def get_instance_counter():
    global instance_counter
    return instance_counter


def get_additional_lines():
    global additional_lines
    return additional_lines
