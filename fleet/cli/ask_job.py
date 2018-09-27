import json
import pdb

cwl2jsonmap = {
  "none": 'null',
  "boolean": 'boolean',
  "int": 'integer',
  "long": 'number',
  "float": 'number',
  "double": 'number',
  "string": 'string',
  "File": 'object',
  "Directory": 'object',
  # 'class' synonymous to 'type'
  "class": "type"
}

exclude = ['inputBinding', 'path', 'baseCommand']
req_fields = []
inputs = []
req = {}

def ask_wkflow(required, optional):
    """Method used to ask users for inputs to a job (.yml) file for use with
    the cwl-runner. Returns the output in dictionary form for easy input into
    templated job files.

    :param dict required: dict of required inputs
    :param dict optional: dict of optional inputs

    example of required(optional):

    {file: {type: File}, message: {type: string}}"""

    # if a requirement has a given type in here, insert this field with it
    fields = {
        'File': 'path'
    }

    out = {}
    # iterate keys to get required fields out of the dict
    for k, v in required.items():
        m = '"{}" is a required field, with type "{}". '.format(k, v['type'])+\
            'Please provide a value for it: '
        inp = None
        while not inp: # users cannot continue unless they enter a value
            inp = input(m)
            if v['type'] in fields.keys():
                insert = fields[v['type']] # get value and use as nested key
                out[k] = {insert: inp}
            else:
                out[k] = inp # assign key-value
    for k, v in optional.items():
        m = '"{}" is an optional input of type "{}"; '.format(k, v['type'])+\
            'Provide an input, or press [Enter] to skip.'
        inp = input(m)
        if inp:
            if v['type'] in fields.keys():
                insert = fields[v['type']].keys()[0]
                out[k] = fields[v['type']][insert] = inp # assign it 
            else:
                out[k] = inp # assign key-value
        else:
            continue # don't need to create it
    return out

def ask(cwl, out):
    """Method used to ask users for inputs to a job (.yml) file for use with
    the cwl-runner. Returns the output in dictionary form for easy input into
    templated job files.

    :param dict cwl: cwl file in dict format
    :param dict out: dict to write to"""

    # iterate keys to get required fields out of the dict
    for inp in cwl.keys():
        if (isinstance(cwl[inp], dict) and inp not in exclude): # call recursively
            if inp == 'properties':
                ask(cwl[inp], out)
                continue # continue in loop w/o nesting
            out.update({inp: {}}) # use this key as outer key, creater nest
            ask(cwl[inp], out[inp]) # pass the updated, nested dict back in
        if not isinstance(cwl[inp], list): # 'required' is always a list
            continue # in the loop, not 'continue to the next step'
        # ask to provide an input
        for field in cwl[inp]:
            m = 'Please provide an input value for "{}": '.format(field)
            out.update({field: input(m)}) 
            
    out = stripper(out)
    return out

def stripper(data):
    """Strip empty key-value pairs from a dict
    :param dict data: dict to strip"""

    new_data = {}
    for k, v in data.items():
        if isinstance(v, dict):
            v = stripper(v)
        if not v in (u'', None, {}):
            new_data[k] = v
    return new_data
