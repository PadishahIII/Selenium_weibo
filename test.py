import re

file = open("test", 'r')
str = file.read()
print(str)
if (str == r'<div class=\"WB_text W_f14\"  div>'):
    print('aa')
rst = re.compile(r'<div class=.{0,2}WB_text W_f14.*div>')
result = rst.findall(str)
print(len(result))

str.replace()