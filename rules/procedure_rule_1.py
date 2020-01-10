#################################################
#   Procedure rule 1: Transformations on        #
#   Recursive Procedures                        #
#   -----------------------------------------   #
#   Iterative algorithms should always be       #
#   preferred to recursive ones.                #
#################################################

import pprint

additional_lines = 0
instance_counter = 0


def check_rule(file_content, function_statements, function_key, function_args, function_location):
    global additional_lines, instance_counter
    additional_lines = 0

    if function_key is None:
        # constructor
        return False

    for statement in function_statements:
        if statement_contains_function_call(statement, function_key, function_args):
            add_comment_above(file_content, function_location)
            pprint.pprint('############# Found potential instance of procedure rule 1: Recursive Procedure')
            pprint.pprint('line: ' + str(function_location['start']['line']))
            instance_counter += 1
            return True


def statement_contains_function_call(statement, function_key, function_args):
    if statement is None or isinstance(statement, str): # happens when there is only a ';'
        return False
    if statement.type == 'IfStatement':
        # check condition
        if statement.TrueBody is not None:
            # check true body
            if statement_contains_function_call(statement.TrueBody, function_key, function_args):
                return True
        if statement.FalseBody is not None:
            # check false body
            if statement_contains_function_call(statement.FalseBody, function_key, function_args):
                return True
    elif statement.type == 'VariableDeclarationStatement':
        if statement.initialValue:
            if statement_contains_function_call(statement.initialValue, function_key, function_args):
                return True
    elif statement.type == 'BinaryOperation':
        # check left
        if statement_contains_function_call(statement.left, function_key, function_args):
            return True
        # check right
        if statement_contains_function_call(statement.right, function_key, function_args):
            return True
    elif statement.type == 'ForStatement':
        if statement_contains_function_call(statement.body, function_key, function_args):
            return True
    elif statement.type == 'Block':
        for block_statement in statement.statements:
            if statement_contains_function_call(block_statement, function_key, function_args):
                return True
    elif statement.type == 'FunctionCall':
        try:
            if statement.expression.name == function_key and len(statement.arguments) == len(function_args):
                # TODO: check type match
                return True
        except KeyError:
            return False
    return False


def add_comment_above(file_content, function_location):
    global additional_lines
    function_line = function_location['start']['line'] - 1 + additional_lines
    tabs_to_insert = ' ' * function_location['start']['column']
    new_line = '// ############ PY_SOLOPT: Found a POSSIBLE instance of a recursive procedure. ' \
               'Please verify.   ############\n'
    new_line2 = '// ############ PY_SOLOPT: If this is the case, remove recursion in order to ' \
                'decrease gas cost. ############\n'
    file_content.insert(function_line, tabs_to_insert + new_line2)
    file_content.insert(function_line, tabs_to_insert + new_line)
    additional_lines += 2


def statement_contains_function_key(file_content, statement, function_key):
    start_line = statement.loc['start']['line'] - 1
    end_line = statement.loc['end']['line']

    for line in range(start_line, end_line):
        content_line = file_content[line]
        if function_key in content_line:
            return True


def get_instance_counter():
    global instance_counter
    return instance_counter
