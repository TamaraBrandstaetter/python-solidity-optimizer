import sys
import pprint

from solidity_parser import parser

from loop_code_motion import check_loop_rule_1


def statement_contains_identifier(loop_statement, variable_name):
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


# find function calls that do not contain the identifier
def assignment_right_side_contains_identifier(loop_statement, variable_name):
    if loop_statement.type == 'ExpressionStatement':
        initial_value = loop_statement.expression
    else:
        return False
    right_side = initial_value.right
    pprint.pprint(right_side)
    if right_side.type == 'BinaryOperation':
        if right_side.left.type == 'FunctionCall':
            pprint.pprint(right_side.left.expression.name)
        if right_side.right.type == 'FunctionCall':
            pprint.pprint(right_side.right.expression.name)
    elif right_side.type == 'FunctionCall':
        pprint.pprint(right_side.expression.name)
    # pprint.pprint(right_side)


def identifier_is_loop_variable(initial_value, variable_name):
    return initial_value.name == variable_name


def binary_operation_contains_identifier(initial_value, variable_name):
    # check left part only if not part of an declaration
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


def main():
    # read input
    file = open(sys.argv[1], "r")
    text = file.read()
    source_unit = parser.parse(text=text, loc=True)
    source_unit_object = parser.objectify(source_unit)
    contracts = source_unit_object.contracts.keys()

    # create output file
    input_file = open(sys.argv[1], "r")
    output_file = open('output.sol', 'w')
    content = input_file.readlines()

    loop_count = 0

    # process rules
    for contract in contracts:
        functions = source_unit_object.contracts[contract].functions
        function_keys = source_unit_object.contracts[contract].functions.keys()
        for file in function_keys:
            file = functions[file]
            statements = file._node.body.statements
            for statement in statements:
                if statement.type == 'ForStatement':
                    # Rule 2 check: Code Motion of Loops
                    check_loop_rule_1(content, statement)

                    loop_count += 1
                    pprint.pprint("-----------------------------------------")
                    # loop_location = statement.loc
                    # loop_expressions = statement.initExpression
                    # loop_body = statement.body
                    # for variable in loop_expressions.variables:
                    #     for loop_statement in loop_body.statements:
                    #         if not statement_contains_identifier(loop_statement, variable.name):
                    #             pprint.pprint("############ found instance of rule #2 #############")
                    #
                    #             tabs_to_insert = '\t' * loop_location['start']['column']
                    #             loop_line = loop_location['start']['line'] - 1
                    #             line_to_move = loop_statement.loc['start']['line'] - 1
                    #             statement_start = loop_statement.loc['start']['column']
                    #             statement_end = loop_statement.loc['end']['column']
                    #
                    #             pprint.pprint(loop_statement.loc)
                    #
                    #             statement_to_insert = tabs_to_insert + content[line_to_move][statement_start:statement_end + 1]
                    #             pprint.pprint(statement_to_insert)
                    #             content.remove(content[line_to_move])
                    #             content.insert(loop_line, statement_to_insert + "\n")
                    #         elif not assignment_right_side_contains_identifier(loop_statement, variable.name):
                    #             pprint.pprint("############ found instance of rule #2 #############")

    pprint.pprint("********************************************")
    pprint.pprint("***********  For-Loops found: " + str(loop_count) + "  ***********")
    pprint.pprint("********************************************")

    # write output
    # content = "".join(content)
    output_file.writelines(content)
    # output_file.write(content)
    output_file.close()

    # pprint.pprint(source_unit_object.contracts['Test'].functions["doSomething1"].parameters)


if __name__ == "__main__":
    main()