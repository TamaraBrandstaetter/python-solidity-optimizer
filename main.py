import sys
import os
import ntpath
import csv
import requests

from solidity_parser import parser

# from rules.logic_rule_1 import check_logic_rule_1
from rules.loop_rule_1 import check_loop_rule_1, get_instance_counter
from rules.loop_rule_2 import check_loop_rule_2
# from rules.loop_rule_3 import check_loop_rule_3
# from rules.loop_rule_4 import check_loop_rule_4
# from rules.loop_rule_5 import check_loop_rule_5
# from rules.procedure_rule_1 import check_procedure_rule_1
# from rules.time_for_space_rule_1 import check_time_for_space_rule_1


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '-initialize':
        initialize()
        return 0
    else:
        files = []
        for r, d, f in os.walk("contracts"):
            for file in f:
                files.append(os.path.join(r, file))

        for_count = 1

        for f in files:
            print(f)
            # read input
            file = open(f, "r", encoding='utf8')
            text = file.read()
            # TODO: replace all \t characters with spaces
            try:
                source_unit = parser.parse(text=text, loc=True)
            except (TypeError, AttributeError):
                continue
            source_unit_object = parser.objectify(source_unit)
            contracts = source_unit_object.contracts.keys()

            # create output file
            input_file = open(f, "r", encoding='utf8')
            output_file = open('output\\opt_' + ntpath.basename(f), 'w', encoding='utf8')
            content = input_file.readlines()

            # get all functions from all contracts in the file
            all_functions = {}
            for contract in contracts:
                function_dictionary = source_unit_object.contracts[contract].functions
                all_functions = {**all_functions, **function_dictionary}

            # process rules
            for contract in contracts:
                # check_time_for_space_rule_1(content, contract)
                functions = source_unit_object.contracts[contract].functions
                function_keys = source_unit_object.contracts[contract].functions.keys()
                for function in function_keys:
                    function = functions[function]
                    # check_logic_rule_1(content, function)
                    # check_procedure_rule_1(content, function)
                    function_body = function._node.body
                    if function_body:
                        statements = function_body.statements
                        for statement in statements:
                            if isinstance(statement, str):
                                # would result in an AttributeError when there is no statement type. example: 'throw;'
                                continue
                            if statement and statement.type == 'ForStatement':
                                for_count += 1
                                check_loop_rule_1(content, statement, all_functions)
                                # check_loop_rule_2(content, statement)
                                # check_loop_rule_3(content, statement)
                                # check_loop_rule_4(content, statement)
                                # check_loop_rule_5(content, statement)
            # write output
            output_file.writelines(content)
            output_file.close()
        # print summary of the findings
        print('# of for statements found in all contracts: ' + str(for_count))
        print('# of instances loop rule 2: ' + str(get_instance_counter()))


def initialize():
    with open('export-verified-contractaddress-opensource-license.csv') as csv_file:
        read_csv = csv.reader(csv_file, delimiter=',')
        addresses = []
        names = []
        skip = 2
        for row in read_csv:
            if skip > 0:
                skip -= 1
            else:
                addresses.append(row[1])
                names.append(row[2])

    # get contracts from api
    url = "https://api.etherscan.io/api"
    api_key = "EMSUR6UBYCTVHFA787RJGBATX7HUHXARZI"
    index = 0
    for address in addresses:
        print(str(index+1) + "/" + str(len(addresses)) + ": " + names[index] + "; address: " + address)
        params = {'module': 'contract', 'action': 'getsourcecode', 'address': address, 'apikey': api_key}
        request = requests.get(url=url, params=params)
        data = request.json()
        output_file = open('contracts\\' + names[index] + '.sol', 'w', encoding='utf8')
        file_content = data['result'][0]['SourceCode'].replace("\r\n", "\n")
        output_file.write(file_content)
        output_file.close()
        index += 1


if __name__ == "__main__":
    main()