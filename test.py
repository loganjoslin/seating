def sort_dict_by_values_reverse(d):
    return dict(sorted(d.items(), key=lambda item: item[1], reverse=True))

# Example usage
d = {'banana': 3, 'apple': 4, 'pear': 1, 'orange': 2}
sorted_by_values_reverse = sort_dict_by_values_reverse(d)
print(sorted_by_values_reverse)