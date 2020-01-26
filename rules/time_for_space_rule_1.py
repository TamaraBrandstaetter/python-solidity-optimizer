#################################################
#   Time-for-space rule 1: Packing              #
#   -----------------------------------------   #
#   Storage can be reused, saving 15,000        #
#   amounts of gas per reuse.                   #
#################################################

import pprint

additional_lines = 0
instance_counter = 0


def check_rule(added_lines, file_content, statements):
    global additional_lines
    additional_lines = added_lines

    variable_declarations = get_declarations(statements)
    get_usages(variable_declarations, statements)

    # suche alle VariableDeclarations auf Ebene 0
    # Gruppiere diese Variablen nach Typ
    # Check verwendung jeder variablen (Ebenen)
    # z.B.  Variable 1 wird verwendet auf Ebene 0, Ebene 1, Ebene 2.
    #       Variable 2 wird verwendet auf Ebene 3, Ebene 4
    #       -> Variable 2 kann durch Variable 1 ersetzt werden.

    return additional_lines


def get_declarations(statements):
    variable_declarations = {}
    for statement in statements:
        if statement.type == 'VariableDeclarationStatement':
            for variable in statement.variables:
                if variable.typeName.type == 'ElementaryTypeName':
                    if variable.typeName.name in variable_declarations:
                        variable_declarations[variable.typeName.name].append(variable.name)
                    else:
                        variable_declarations[variable.typeName.name] = [variable.name]
    return variable_declarations


def get_usages(variable_declarations, statements):
    # kick out all variable types that occur only once
    to_delete = []
    for declaration in variable_declarations:
        if len(variable_declarations[declaration]) == 1:
            to_delete.append(declaration)
        else:
            print('### found possible packing for variable type: ' + str(declaration))
            print('### variables of type ' + str(declaration)+ ": " + ",".join(variable_declarations[declaration]))
    for var_type in to_delete:
        del variable_declarations[var_type]

    # var_usages = {}
    # for var_type in variable_declarations:
    #     var_usage_layer = {}
    #     for var in variable_declarations[var_type]:
    #         var_usage_layer[var] = get_usage_layer(var, statements, 1)
    #         # search for simultaneous usages of variables of same type
    #     var_usages[var_type] = var_usage_layer
    # return var_usages


def get_usage_layer(var, statements, start_layer):
    layer = 0
    for statement in statements:
        # if statement starts a new layer:
        if statement.type == 'ForStatement':
            # check condition and stuff
            if layer < start_layer:
                if statement.initExpression is not None and is_used_in_statement(var, statement.initExpression):
                    if layer < start_layer:
                        layer += start_layer
                if statement.conditionExpression is not None and is_used_in_expression(var, statement.conditionExpression):
                    if layer < start_layer:
                        layer += start_layer
                if statement.loopExpression is not None and is_used_in_statement(var, statement.loopExpression):
                    if layer < start_layer:
                        layer += start_layer
            # next_statements = statements # todo
            if statement.body is not None and statement.body.type == 'Block':
                layer += get_usage_layer(var, statement.body.statements, start_layer * 10)
        elif statement.type == 'IfStatement':
            # check condition
            next_statements = statements # todo
            layer += get_usage_layer(var, next_statements, start_layer * 10)
        # if is used in statement:
        elif is_used_in_statement(var, statement):
            if layer < start_layer:
                layer += start_layer
    return layer


def is_used_in_statement(var, statement):
    if statement.type == 'VariableDeclarationStatement':
        return is_used_in_declaration(var, statement)
    elif statement.type == 'Identifier':
        return statement.name == var
    elif statement.type == 'NumberLiteral' or statement.type == 'StringLiteral' or statement.type == 'HexLiteral' \
            or statement.type == 'BooleanLiteral':
        return False
    elif statement.type == 'ExpressionStatement':
        return is_used_in_expression(var, statement.expression)
    # default return True to avoid false positives
    return True


def is_used_in_expression(var, expression):
    if expression.type == 'BinaryOperation':
        return is_used_in_expression(var, expression.left) or is_used_in_expression(var, expression.right)
    elif expression.type == 'Identifier':
        return expression.name == var
    elif expression.type == 'NumberLiteral' or expression.type == 'StringLiteral' or expression.type == 'HexLiteral' \
            or expression.type == 'BooleanLiteral':
        return False
    return True


def is_used_in_declaration(var, statement):
    if statement.initialValue is not None:
        return is_used_in_statement(var, statement.initialValue)
    return False



















# def is_used(var, statements, stage):
#     stage_value = 0
#     for statement in statements:
#         # ebene 0
#         if stage_value != stage:
#             # check on same ebene
#             if statement.type == 'VariableDeclarationStatement' and statement.initialValue is not None:
#                 if is_used_in_expression(var, statement.initialValue, stage):
#                     if stage_value != stage:
#                         stage_value = stage
#             elif statement.type == 'ExpressionStatement':
#                 if is_used_in_expression(var, statement.expression, stage):
#                     stage_value = stage
#         if statement.type == 'IfStatement':
#             # ebene +1
#             continue
#         elif statement.type == 'ForStatement' and statement.body:
#             # ebene +1
#             # initExpression, conditionExpression or loopExpression uses var?
#             # return 1 + is_used(var, statements, stage * 10)
#             stage_value += is_used(var, statement.body.statements, stage * 10)
#         elif statement.type == 'WhileStatement':
#             # ebene +1
#             continue
#         elif statement.type == 'DoWhileStatement':
#             continue
#         # elif statement.type == 'FunctionCall':
#         #     continue
#         # else:
#         #     continue
#     return stage_value
#
#
# # def is_used_in_statement(var, statement, stage):
# #     if statement.type == 'VariableDeclarationStatement' and statement.initialValue is not None:
# #         is_used_in_statement(var, statement.initialValue, stage)
# #     if statement.type == 'Identifier':
# #         is_used_in_expression(var, statement, stage)
#
#
# def is_used_in_expression(var, expression, stage):
#     if expression.type == 'BinaryOperation':
#         return used_in_binary_operation(var, expression, stage)
#     # elif expression.type == 'FunctionCall':
#     #     return used_in_function_call(var, expression, stage)
#     elif expression.type == 'Identifier':
#         return used_in_identifier(var, expression, stage)
#     # elif expression.type == 'IndexAccess':
#     #     return used_in_index_access(var, expression, stage)
#     # elif expression.type == 'TupleExpression':
#     #     return used_in_expression(var, expression, stage)
#     # elif expression.type == 'MemberAccess':
#     #     return is_used_in_expression(var, expression, stage)
#     return 0
#
#
# def used_in_binary_operation(var, expression, stage):
#     left_expr = expression.left
#     right_expr = expression.right
#     if is_used_in_expression(var, left_expr, stage) or is_used_in_expression(var, right_expr, stage):
#         return stage
#     return 0
#
#
# def used_in_identifier(var, expression, stage):
#     if expression.name == var:
#         return stage
#     return 0
#
#



def get_instance_counter():
    global instance_counter
    return instance_counter


def get_additional_lines():
    global additional_lines
    return additional_lines
