""" Utility functions for webscraper"""
import json

def output_json(input_quotes, name):
    """outputs and prettifys quotes to json file"""
    filename = './' + name + '.json'
    json.dump(input_quotes, open(filename, 'w'), indent=4, sort_keys=True)
    print('\nQuotes are in ' + name + '.json')

def validate_name(name):
    """Return True if valid name, else return False"""
    bad_chars = ['.', "\\", "/", "*", "?", '"', "<", ">", "|"]
    if any(i in name for i in bad_chars):
        print('Filename cannot contain these characters: ' + '[ ' + ', '.join(bad_chars) + ' ]')
        return False
    return True
    