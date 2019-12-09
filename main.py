import sys
import pprint

from solidity_parser import parser

from loop_rule_1 import check_loop_rule_1


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
                    check_loop_rule_1(content, statement, functions)
                    # check_loop_rule_2(content, statement)
                    # check_loop_rule_3(content, statement)
                    # check_loop_rule_4(content, statement)
                    # check_loop_rule_5(content, statement)
                    # check_time_for_space_rule_1(content, statement)
                    # check_logic_rule_1(content, statement)
                    # check_procedure_rule_1(content, statement)
    # write output
    output_file.writelines(content)
    output_file.close()


if __name__ == "__main__":
    main()