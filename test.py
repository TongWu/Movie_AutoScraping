test = []
prefix_number = '332'
prefix = 'ssni'
number = 231
test = [prefix_number, prefix, number, 'C']
#str_test = '-'.join(str(item) for item in test)
first_item = str(test[0])
remaining_items = '-'.join(str(item) for item in test[1:])
result = f"{first_item}{remaining_items}"
print(result)