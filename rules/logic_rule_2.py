##################################################
#   Logic rule 1: Boolean Variable Elimination   #
#   -------------------------------------------  #
#   Direct evaluation of the condition instead   #
#   of storing the result in a boolean variable. #
##################################################

import pprint

instance_counter = 0
missing_lines = 0


def check_rule(file_content, function_statements, statement):
    global missing_lines
    missing_lines = 0
    # Statement = bool variable declaration
    for function_statement in function_statements:
        if function_statement == statement:
            continue
        if function_statement.type == 'IfStatement' and function_statement.condition.type == 'Identifier':
            for variable in statement.variables:
                if function_statement.condition.name == variable.name and statement.initialValue:
                    # if the value is not modified afterwards
                    if not variable_is_modified_afterwards(function_statements, function_statement, statement, variable.name):
                        pprint.pprint("#### found instance of logic rule 2")
                        eliminate_bool_variable(file_content, statement, function_statement)
    return file_content


def variable_is_modified_afterwards(function_statements, if_statement, variable_declaration, variable_name):
    before_declaration = True
    for statement in function_statements:
        if before_declaration and statement == variable_declaration:
            before_declaration = False
            continue
        if statement == if_statement:
            # was not used until now, return False
            return False
        # check whether variable_name is used inside the statement
        if statement_changes_variable(statement, variable_name):
            return True
    return False


def statement_changes_variable(statement, variable_name):
    if statement.type == 'VariableDeclarationStatement':
        for variable in statement.variables:
            if variable.name == variable_name:
                return True
    return True


def eliminate_bool_variable(file_content, statement, if_statement):
    global instance_counter, missing_lines
    instance_counter += 1

    statement_line = statement.loc['start']['line'] - 1 - missing_lines
    pprint.pprint('bool variable line: ' + str(statement_line))

    if_statement_line = if_statement.loc['start']['line'] - 1 - missing_lines
    pprint.pprint('if statement line: ' + str(if_statement_line))

    condition_start = if_statement.condition.loc['start']['column']
    condition_end = if_statement.condition.loc['end']['column'] + len(if_statement.condition.name)

    statement_location_start = statement.initialValue.loc['start']['column']
    statement_location_end = statement.initialValue.loc['end']['column'] + 1

    statement_to_move = file_content[if_statement_line][condition_start:condition_end]
    replacement = file_content[statement_line][statement_location_start:statement_location_end]

    new_line = file_content[if_statement_line].replace(statement_to_move, replacement)
    file_content.remove(file_content[if_statement_line])
    file_content.insert(if_statement_line, new_line)
    file_content.remove(file_content[statement_line])
    missing_lines += 1


def get_instance_counter():
    global instance_counter
    return instance_counter