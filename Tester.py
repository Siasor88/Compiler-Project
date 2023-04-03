import re
Tests_num = 10
for i in range(1,Tests_num+1):
    print("Test", i, "of", Tests_num)
    f1 = open('./PA1_testcases/T' + ('0'+str(i) if i < 10 else str(i)) + '/lexical_errors.txt', 'r')
    f2 = open('./PA1_testcases/T' + ('0'+str(i) if i < 10 else str(i)) + '/result_lexical_errors.txt', 'r')
    print("Lexical Errors:")

    if re.sub(r'\s+', '', f1.read()) == re.sub(r'\s+', '', f2.read()):
        print("Passed")
    else:
        print("Failed")
        #print the different lines between the two files with the line numbers
        f1.seek(0)
        f2.seek(0)
        line_num = 1
        for line1, line2 in zip(f1, f2):
            if line1 != line2:
                print("Line", line_num, ":", line1, "should be", line2)
            line_num += 1
    f1.close()
    f2.close()
    f1 = open('./PA1_testcases/T' + ('0'+str(i) if i < 10 else str(i)) + '/tokens.txt', 'r')
    f2 = open('./PA1_testcases/T' + ('0'+str(i) if i < 10 else str(i)) + '/result_tokens.txt', 'r')
    print("Tokens:")
    if re.sub(r'\s+', '', f1.read()) == re.sub(r'\s+', '', f2.read()):
        print("Passed")
    else:
        print("Failed")
        #print the different lines between the two files with the line numbers
        f1.seek(0)
        f2.seek(0)
        line_num = 1
        for line1, line2 in zip(f1, f2):
            if line1 != line2:
                print("Line", line_num, ":", line1, "should be", line2)
            line_num += 1
    f1.close()
    f2.close()
    print("__________________________________________________________")