#################################################
#   loop rule 1: Code motion of loops           #
#   -----------------------------------------   #
#   Repeated calculations are moved outside a   #
#   loop and therefore only calculated once.    #
#################################################

import uuid

additional_lines = 0
instance_counter = 0


def check_rule(added_lines, file_content, loop_statement, functions):
    global additional_lines
    additional_lines = added_lines
    loop_expressions = loop_statement.initExpression
    loop_body = loop_statement.body
    loop_location = loop_statement.loc

    if loop_expressions is None:
        # no loop expression. example: "for (; len >= 32; len -= 32)"
        return additional_lines
    try:
        loop_expressions.variables
    except KeyError:
        # loop variable is not defined inside the loop. example: "for (i = 0; i < length; i++)"
        return additional_lines
    for variable in loop_expressions.variables:
        if loop_body.type == 'Block':
            for loop_statement in loop_body.statements:
                if not isinstance(loop_statement, str) and loop_statement.type == 'VariableDeclarationStatement':
                    move_statement_up(file_content, loop_statement, loop_location, variable.name, functions, loop_body)
        elif loop_body.type == 'ExpressionStatement':
            # loop inline. example: "for (uint i = 0; i < _ba.length; i++) babc[k++] = _ba[i];"
            return additional_lines
    return additional_lines


def move_statement_up(file_content, loop_statement, loop_location, variable_name, functions, loop_body):
    global instance_counter
    loop_line = loop_location['start']['line'] - 1 + additional_lines
    tabs_to_insert = ' ' * loop_location['start']['column']

    if not statement_contains_identifier(loop_statement, variable_name) \
            and not statement_contains_identifiers_modified_inside_loop(loop_statement, loop_body):
        # none of the parts on the right side are modified inside the loop
        # example: for (uint256 i = 0; i < pow; i++) {
        #             uint256 previousResult = result; # can't move this line up
        #             result = previousResult.mul(a);
        #         }
        print('### found instance of loop rule 1; line: ' + str(loop_line))
        instance_counter += 1

        line_to_move = loop_statement.loc['start']['line'] - 1 + additional_lines
        statement_start = loop_statement.loc['start']['column']
        statement_end = loop_statement.loc['end']['column'] + 1
        statement_to_insert = tabs_to_insert + file_content[line_to_move][statement_start:statement_end]
        del file_content[line_to_move]
        file_content.insert(loop_line, statement_to_insert + "\n")
    elif statement_contains_pure_function_call(file_content, loop_location, loop_statement, variable_name, functions):
        print('### found instance of loop rule 1 in function call')
        instance_counter += 1


def statement_contains_pure_function_call(file_content, loop_location, loop_statement, variable_name, functions):
    if isinstance(loop_statement, str):
        # would result in an AttributeError when there is no statement type. example: 'throw;' or 'break;'
        return False
    if loop_statement.type == 'ExpressionStatement':
        initial_value = loop_statement.expression
    else:
        return False
    if initial_value.type == 'BinaryOperation':
        return check_for_pure_function_call(file_content, loop_location, initial_value.right, functions)
    else:
        return False


# loop statement = the statement we want to move up
def statement_contains_identifiers_modified_inside_loop(loop_statement, loop_body):
    # for all variables inside the loop check:
    temp = True
    for body_statement in loop_body.statements:
        if loop_statement == body_statement:
            continue
        if isinstance(body_statement, str):
            # would result in an AttributeError when there is no statement type. example: 'throw;' or 'break;'
            continue
        if body_statement.type == 'VariableDeclarationStatement' and body_statement.variables is not None:
            for variable in body_statement.variables:
                if not statement_contains_identifier(loop_statement, variable.name):
                    continue
                else:
                    return True
        elif body_statement.type == 'ExpressionStatement':
            if body_statement.expression.type == 'BinaryOperation':
                if body_statement.expression.left.type == 'Identifier' \
                        and body_statement.expression.left.name != loop_statement.variables[0].name \
                        and not statement_contains_identifier(loop_statement, body_statement.expression.left.name):
                    continue
                elif body_statement.expression.left.type == 'TupleExpression':
                    for component in body_statement.expression.left.components:
                        if component and component.type == 'Identifier' \
                                and component.name != loop_statement.variables[0].name \
                                and not statement_contains_identifier(loop_statement, component.name):
                            continue
                        elif component and component.name == loop_statement.variables[0].name:
                            return True
                elif body_statement.expression.left.type == 'IndexAccess':
                    if body_statement.expression.left.base.type == 'Identifier' \
                            and body_statement.expression.left.base.name != loop_statement.variables[0].name:
                        continue
                else:
                    temp = False
        elif body_statement.type == 'IfStatement':
            if body_statement.TrueBody is not None \
                    and not isinstance(body_statement.TrueBody, str) \
                    and body_statement.TrueBody.type == 'Block':
                if statement_contains_identifiers_modified_inside_loop(loop_statement, body_statement.TrueBody):
                    return True
                else:
                    continue
            else:
                return True
        elif body_statement.type == 'ForStatement':
            if body_statement.body is not None and body_statement.body.type == 'Block':
                if statement_contains_identifiers_modified_inside_loop(loop_statement, body_statement.body):
                    return True
                else:
                    continue
            else:
                return True
        else:
            temp = False
    if not temp:
        return True
    return False


def check_for_pure_function_call(file_content, loop_location, statement, functions):
    if statement.type == 'BinaryOperation':
        check_for_pure_function_call(file_content, loop_location, statement.left, functions)
        check_for_pure_function_call(file_content, loop_location, statement.right, functions)
    elif statement.type == 'FunctionCall':
        try:
            function_name = statement.expression.name
            function = functions[function_name]
        except KeyError:
            return False
        if function.stateMutability in ['pure', 'view', 'constant'] and function.arguments == {}:
            global additional_lines
            loop_line = loop_location['start']['line'] - 1 + additional_lines
            tabs_to_insert = ' ' * loop_location['start']['column']
            statement_line = statement.loc['start']['line'] - 1 + additional_lines
            statement_start = statement.loc['start']['column']
            statement_end = statement.loc['end']['column'] + 1
            statement_to_move = file_content[statement_line][statement_start:statement_end]
            variable_name = "var_" + str(uuid.uuid4()).replace("-", "")
            return_type = function._node.returnParameters.parameters[0].typeName.name
            new_line = file_content[statement_line].replace(statement_to_move, variable_name)
            del file_content[statement_line]
            file_content.insert(statement_line, new_line)
            file_content.insert(loop_line,
                                tabs_to_insert + return_type + " " + variable_name + " = " + statement_to_move + ";\n")
            comment_line = '// ############ PY_SOLOPT: Found instance of the rule Code motion of loops. ############\n'
            file_content.insert(loop_line, comment_line)
            additional_lines += 2
            return True
    return False


def statement_contains_identifier(loop_statement, variable_name):
    if isinstance(loop_statement, str):
        # would result in an AttributeError when there is no statement type. example: 'throw;' or 'break;'
        return False
    if loop_statement.type == 'VariableDeclarationStatement':
        initial_value = loop_statement.initialValue
    elif loop_statement.type == 'ExpressionStatement':
        initial_value = loop_statement.expression
    else:
        return True
    # as identifier
    if initial_value is None:  # no value set; example: "uint256 a;"
        return False
    elif initial_value.type == 'Identifier':
        return identifier_is_loop_variable(initial_value, variable_name)
    # as part of an operation
    elif initial_value.type == 'BinaryOperation':
        return binary_operation_contains_identifier(initial_value, variable_name)
    elif initial_value.type == 'NumberLiteral' \
            or initial_value.type == 'StringLiteral' \
            or initial_value.type == 'HexLiteral' \
            or initial_value.type == 'BooleanLiteral':
        return False
    else:
        pass
    return True


def identifier_is_loop_variable(initial_value, variable_name):
    return initial_value.name == variable_name


def tuple_expression_contains_identifier(tuple, variable_name):
    for component in tuple.components:
        return check_side_of_binary_operation(component, variable_name)
    return False


def index_accesses_loop_variable(index_access, variable_name):
    if index_access.type == 'IndexAccess':
        if index_access.base.type == 'Identifier' and index_access.base.name == variable_name:
            return True
        return statement_contains_identifier(index_access.index, variable_name)
    elif index_access.type == 'Identifier' and index_access.name == variable_name:
        return True
    return False


def binary_operation_contains_identifier(initial_value, variable_name):
    return check_side_of_binary_operation(initial_value.left, variable_name) \
           or check_side_of_binary_operation(initial_value.right, variable_name)


def check_side_of_binary_operation(side, variable_name):
    if side.type == 'BinaryOperation':
        return binary_operation_contains_identifier(side, variable_name)
    elif side.type == 'Identifier':
        return identifier_is_loop_variable(side, variable_name)
    elif side.type == 'TupleExpression':
        return tuple_expression_contains_identifier(side, variable_name)
    elif side.type == 'IndexAccess':
        return index_accesses_loop_variable(side, variable_name)
    elif side.type == 'NumberLiteral' \
            or side.type == 'StringLiteral' \
            or side.type == 'HexLiteral' \
            or side.type == 'BooleanLiteral':
        return False
    return True


def get_instance_counter():
    global instance_counter
    return instance_counter


def get_additional_lines():
    global additional_lines
    return additional_lines
