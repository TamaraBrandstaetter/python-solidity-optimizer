# this is used for evaluation only
# several metrics are calculated
import os

from solidity_parser import parser

de_morgan_counter = 0
binary_if_statement_counter = 0


def get_files():
    files = []
    for r, d, f in os.walk("contracts"):
        for file in f:
            files.append(os.path.join(r, file))
    return files


def count_de_morgan():
    for f in get_files():
        print(f)
        file = open(f, "r", encoding='utf8')
        text = file.read()
        try:
            source_unit = parser.parse(text=text, loc=True)
        except (TypeError, AttributeError):
            continue
        source_unit_object = parser.objectify(source_unit)
        contracts = source_unit_object.contracts.keys()
        for contract in contracts:
            functions = source_unit_object.contracts[contract].functions
            function_keys = source_unit_object.contracts[contract].functions.keys()
            for function_key in function_keys:
                function = functions[function_key]
                function_body = function._node.body
                if function_body:
                    statements = function_body.statements
                    for statement in statements:
                        if isinstance(statement, str):
                            # would result in an AttributeError when there is no statement type. example: 'throw;'
                            continue
                        if statement:
                            if statement.type == 'IfStatement':
                                check_if_statement(statement)
    print('##############################################')
    print('applied de morgan law found: ' + str(de_morgan_counter))
    print('binary operation without negation in if statement found: ' + str(binary_if_statement_counter))


def check_if_statement(statement):
    global de_morgan_counter, binary_if_statement_counter
    if statement.condition.type == 'BinaryOperation':
        if statement.condition.operator == '&&' or statement.condition.operator == '||' \
                and statement.condition.left.type != 'UnaryOperation' \
                and statement.condition.right.type != 'UnaryOperation':
            statement_line = statement.loc['start']['line'] - 1
            print('##### found binary operation without negation in if statement; line: ' + str(statement_line))
            binary_if_statement_counter += 1
    elif statement.condition.type == 'UnaryOperation' and statement.condition.operator == '!' \
            and statement.condition.subExpression.type == 'TupleExpression' \
            and statement.condition.subExpression.components \
            and statement.condition.subExpression.components[0].type == 'BinaryOperation' \
            and (statement.condition.subExpression.components[0].operator == '&&'
                 or statement.condition.subExpression.components[0].operator == '||') \
            and statement.condition.subExpression.components[0].left.type != 'UnaryOperation' \
            and statement.condition.subExpression.components[0].right.type != 'UnaryOperation':
        statement_line = statement.loc['start']['line'] - 1
        print('##### found applied de morgan law; line: ' + str(statement_line))
        de_morgan_counter += 1


bool_counter = 0


def count_bool_variables():
    global bool_counter
    for f in get_files():
        print(f)
        file = open(f, "r", encoding='utf8')
        text = file.read()
        try:
            source_unit = parser.parse(text=text, loc=True)
        except (TypeError, AttributeError):
            continue
        source_unit_object = parser.objectify(source_unit)
        contracts = source_unit_object.contracts.keys()
        for contract in contracts:
            functions = source_unit_object.contracts[contract].functions
            function_keys = source_unit_object.contracts[contract].functions.keys()
            for function_key in function_keys:
                function = functions[function_key]
                function_body = function._node.body
                if function_body:
                    statements = function_body.statements
                    for statement in statements:
                        if isinstance(statement, str):
                            # would result in an AttributeError when there is no statement type. example: 'throw;'
                            continue
                        if statement and statement.type == 'VariableDeclarationStatement' and statement.variables \
                                and len(statement.variables) == 1:
                            for variable in statement.variables:
                                if variable.type == 'VariableDeclaration' \
                                        and variable.typeName.type == 'ElementaryTypeName' \
                                        and variable.typeName.name == 'bool':
                                    statement_line = statement.loc['start']['line'] - 1
                                    print('##### found boolean variable; line: ' + str(statement_line))
                                    bool_counter += 1
    print('##############################################')
    print('bool variables found: ' + str(bool_counter))


while_counter = 0
for_counter = 0
do_while_counter = 0


def count_loops():
    global for_counter, while_counter, do_while_counter
    for f in get_files():
        print(f)
        file = open(f, "r", encoding='utf8')
        text = file.read()
        try:
            source_unit = parser.parse(text=text, loc=True)
        except (TypeError, AttributeError):
            continue
        source_unit_object = parser.objectify(source_unit)
        contracts = source_unit_object.contracts.keys()
        for contract in contracts:
            functions = source_unit_object.contracts[contract].functions
            function_keys = source_unit_object.contracts[contract].functions.keys()
            for function_key in function_keys:
                function = functions[function_key]
                function_body = function._node.body
                if function_body:
                    statements = function_body.statements
                    for statement in statements:
                        if statement is None or isinstance(statement, str):
                            # would result in an AttributeError when there is no statement type. example: 'throw;'
                            continue
                        if statement.type in ['ForStatement', 'WhileStatement', 'DoWhileStatement']:
                            check_loop(statement)
                        elif statement.type == 'IfStatement':
                            if statement.TrueBody is not None and not isinstance(statement.TrueBody, str) \
                                    and statement.TrueBody.type == 'Block':
                                # check true body
                                for s in statement.TrueBody.statements:
                                    check_loop(s)
                            if statement.FalseBody is not None and not isinstance(statement.TrueBody, str) \
                                    and statement.FalseBody.type == 'Block':
                                # check false body
                                for s in statement.FalseBody.statements:
                                    check_loop(s)
        print('for loops found: ' + str(for_counter))
        print('while loops found: ' + str(while_counter))
        print('do-while loops found: ' + str(do_while_counter))
    print('##############################################')
    print('for loops found: ' + str(for_counter))
    print('while loops found: ' + str(while_counter))
    print('do-while loops found: ' + str(do_while_counter))


def check_loop(statement):
    global for_counter, while_counter, do_while_counter
    if statement is None or isinstance(statement, str):
        # would result in an AttributeError when there is no statement type. example: 'throw;'
        return
    if statement.type == 'ForStatement':
        for_counter += 1
    elif statement.type == 'WhileStatement':
        while_counter += 1
    elif statement.type == 'DoWhileStatement':
        do_while_counter += 1


one_condition_counter = 0


def count_loop_conditions():
    global one_condition_counter
    for f in get_files():
        print(f)
        file = open(f, "r", encoding='utf8')
        text = file.read()
        try:
            source_unit = parser.parse(text=text, loc=True)
        except (TypeError, AttributeError):
            continue
        source_unit_object = parser.objectify(source_unit)
        contracts = source_unit_object.contracts.keys()
        for contract in contracts:
            functions = source_unit_object.contracts[contract].functions
            function_keys = source_unit_object.contracts[contract].functions.keys()
            for function_key in function_keys:
                function = functions[function_key]
                function_body = function._node.body
                if function_body:
                    statements = function_body.statements
                    for statement in statements:
                        if statement is None or isinstance(statement, str):
                            # would result in an AttributeError when there is no statement type. example: 'throw;'
                            continue
                        if statement.type in ['ForStatement', 'WhileStatement', 'DoWhileStatement']:
                            check_condition(statement)
                        elif statement.type == 'IfStatement':
                            if statement.TrueBody is not None and not isinstance(statement.TrueBody, str) \
                                    and statement.TrueBody.type == 'Block':
                                # check true body
                                for s in statement.TrueBody.statements:
                                    check_condition(s)
                            if statement.FalseBody is not None and not isinstance(statement.TrueBody, str) \
                                    and statement.FalseBody.type == 'Block':
                                # check false body
                                for s in statement.FalseBody.statements:
                                    check_condition(s)
        print('count: ' + str(one_condition_counter))
    print('##############################################')
    print('loops with only one condition found: ' + str(one_condition_counter))


def check_condition(loop_statement):
    global one_condition_counter
    if loop_statement is None or isinstance(loop_statement, str):
        # would result in an AttributeError when there is no statement type. example: 'throw;'
        return
    if loop_statement.type == 'WhileStatement' or loop_statement.type == 'DoWhileStatement':
        if loop_statement.condition is not None and (
                loop_statement.condition.type != 'BinaryOperation' or (loop_statement.condition.operator != '&&'
                                                                       and loop_statement.condition.operator != '||')):
            one_condition_counter += 1
    elif loop_statement.type == 'ForStatement':
        if (
                loop_statement.conditionExpression is not None and loop_statement.conditionExpression.type != 'BinaryOperation'
                or (loop_statement.conditionExpression.operator != '&&'
                    and loop_statement.conditionExpression.operator != '||')):
            one_condition_counter += 1
