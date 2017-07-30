import json
from collections import defaultdict

def output_json(input_quotes, name):
    """outputs and prettifys quotes to json file"""
    filename = './' + name + '.json'
    json.dump(input_quotes, open(filename, 'w'), indent=4, sort_keys=True)
    print('\nQuotes outputted to ' + name + '.json')

def validate_name(name):
    """Return True if valid name, else return False"""
    bad_chars = ['.', "\\", "/", "*", "?", '"', "<", ">", "|"]
    if any(i in name for i in bad_chars):
        print('Filename cannot contain these characters: ' + '[ ' + ', '.join(bad_chars) + ' ]')
        return False
    return True

def combine_dicts(main_dict, list_of_dicts):
    """Combine two dictionaries"""
    for dic in list_of_dicts:
        for key, value in dic.items():
            if key in main_dict:
                main_dict.get(key).extend(value)
            else:
                main_dict[key] = value
                
def combine_list_of_dicts(list_of_dicts):
    super_dict = defaultdict(set)
    for dic in list_of_dicts:
        for key, value in dic.items():
            super_dict[key] = value
    return dict(super_dict)
