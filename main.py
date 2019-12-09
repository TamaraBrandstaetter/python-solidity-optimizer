import sys
import pprint

from solidity_parser import parser

from logic_rule_1 import check_logic_rule_1
from loop_rule_1 import check_loop_rule_1
from loop_rule_2 import check_loop_rule_2
from loop_rule_3 import check_loop_rule_3
from loop_rule_4 import check_loop_rule_4
from loop_rule_5 import check_loop_rule_5
from procedure_rule_1 import check_procedure_rule_1
from time_for_space_rule_1 import check_time_for_space_rule_1


def main():
    # read input
    file = open(sys.argv[1], "r")
    text = file.read()
    # TODO: replace all \t characters with spaces
    source_unit = parser.parse(text=text, loc=True)
    source_unit_object = parser.objectify(source_unit)
    contracts = source_unit_object.contracts.keys()

    # create output file
    input_file = open(sys.argv[1], "r")
    output_file = open('output.sol', 'w')
    content = input_file.readlines()

    # process rules
    for contract in contracts:
        check_time_for_space_rule_1(content, contract)
        functions = source_unit_object.contracts[contract].functions
        function_keys = source_unit_object.contracts[contract].functions.keys()
        for function in function_keys:
            function = functions[function]
            check_logic_rule_1(content, function)
            check_procedure_rule_1(content, function)
            statements = function._node.body.statements
            for statement in statements:
                if statement.type == 'ForStatement':
                    check_loop_rule_1(content, statement, functions)
                    check_loop_rule_2(content, statement)
                    check_loop_rule_3(content, statement)
                    check_loop_rule_4(content, statement)
                    check_loop_rule_5(content, statement)
    # write output
    output_file.writelines(content)
    output_file.close()


if __name__ == "__main__":
    main()