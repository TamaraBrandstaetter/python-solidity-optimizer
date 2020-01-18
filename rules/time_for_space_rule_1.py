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

    # variable_declarations = get_declarations(statements)

    # suche alle VariableDeclarations auf Ebene 0
        # Gruppiere diese Variablen nach Typ
        # Check verwendung jeder variablen (Ebenen)
        # z.B.  Variable 1 wird verwendet auf Ebene 0, Ebene 1, Ebene 2.
        #       Variable 2 wird verwendet auf Ebene 3, Ebene 4
        #       -> Variable 2 kann durch Variable 1 ersetzt werden.

    return additional_lines


def get_usages(variable_declarations, statements):
    var_usages = {}

    for var_type in variable_declarations:
        # search for simultaneous usages of variables of same type
        for statement in statements:
            # ebene 0
            if statement.type == 'VariableDeclarationStatement':
                continue
            elif statement.type == 'ExpressionStatement':
                continue
            elif statement.type == 'IfStatement':
                # ebene +1
                continue
            elif statement.type == 'ForStatement':
                # ebene +1
                continue
            elif statement.type == 'WhileStatement':
                # ebene +1
                continue
            elif statement.type == 'FunctionCall':
                continue
            else:
                continue

    return var_usages


def get_declarations(statements):
    variable_declarations = {}

    for statement in statements:
        if statement.type == 'VariableDeclarationStatement':
            for variable in statement.variables:
                if variable.typeName.name in variable_declarations:
                    variable_declarations[variable.typeName.name].append(variable.name)
                else:
                    variable_declarations[variable.typeName.name] = [variable.name]
    return variable_declarations



def get_instance_counter():
    global instance_counter
    return instance_counter


def get_additional_lines():
    global additional_lines
    return additional_lines
