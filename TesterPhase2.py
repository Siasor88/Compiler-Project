import re


def get_symbol(symbol: str):
    p = re.compile('\d+\.\s+(\w+)')
    return p.search(symbol).group(1)


Tests_num = 10
passed_tests = 0
for i in range(1, Tests_num + 1):
    test_state = True
    print("Test", i, "of", Tests_num)
    f1 = open('./PA2_testcases/T' + ('0' + str(i) if i < 10 else str(i)) + '/parse_tree.txt', 'r')
    f2 = open('./PA2_testcases/T' + ('0' + str(i) if i < 10 else str(i)) + '/parse_tree_result.txt', 'r')
    print("Parse Tree:")
    if re.sub(r'\s+', '', f1.read()) == re.sub(r'\s+', '', f2.read()):
        print("Passed")
    else:
        print("Failed")
        test_state = False
        # print the different lines between the two files with the line numbers
        f1.seek(0)
        f2.seek(0)
        line_num = 1
        for line1, line2 in zip(f1, f2):
            if line1 != line2:
                print("Line", line_num, ":", line1, "should be", line2)
            line_num += 1
    f1.close()
    f2.close()
    # f1 = open('./PA1_testcases/T' + ('0' + str(i) if i < 10 else str(i)) + '/tokens.txt', 'r')
    # f2 = open('./PA1_testcases/T' + ('0' + str(i) if i < 10 else str(i)) + '/result_tokens.txt', 'r')
    # print("Tokens:")
    # if re.sub(r'\s+', '', f1.read()) == re.sub(r'\s+', '', f2.read()):
    #     print("Passed")
    # else:
    #     print("Failed")
    #     test_state = False
    #     # print the different lines between the two files with the line numbers
    #     f1.seek(0)
    #     f2.seek(0)
    #     line_num = 1
    #     for line1, line2 in zip(f1, f2):
    #         if line1 != line2:
    #             print("Line", line_num, ":", line1, "should be", line2)
    #         line_num += 1
    # f1.close()
    # f2.close()
    #
    # f1 = open('./PA1_testcases/T' + ('0' + str(i) if i < 10 else str(i)) + '/symbol_table.txt', 'r')
    # f2 = open('./PA1_testcases/T' + ('0' + str(i) if i < 10 else str(i)) + '/result_symbol_table.txt', 'r')
    #
    # f1_read = f1.read().strip()
    # f2_read = f2.read().strip()
    #
    # f1_elements = f1_read.split('\n')
    # f2_elements = f2_read.split('\n')
    # f1_elements = set([get_symbol(e) for e in f1_elements])
    # f2_elements = set([get_symbol(e) for e in f2_elements])
    # print('Symbols:')
    # if f1_elements == f2_elements:
    #     print("Passed")
    # else:
    #     print("Failed")
    #     test_state = False
    # print("__________________________________________________________")
    if test_state:
        passed_tests += 1
print(f'{passed_tests}/{Tests_num} test passed.')
