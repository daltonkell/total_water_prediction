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

def ask(cwl, out):
    """Method used to ask users for inputs to a job (.yml) file for use with
    the cwl-runner. Returns the output in dictionary form for easy input into
    templated job files.

    :param dict cwl: cwl file in dict format
    :param dict out: dict to write to; default None"""

    # iterate keys to get required fields out of the dict
    for inp in cwl.keys():
        if (isinstance(cwl[inp], dict) and inp not in exclude): # call recursively
            if inp == 'properties':
                ask(cwl[inp], out)
                continue # continue in loop -- we're done with this key
            out.update({inp: {}}) # use this key as outer key, creater inner nest
            ask(cwl[inp], out[inp]) # pass the updated, nested dict back in
        if not isinstance(cwl[inp], list): # 'required' is always a list
            continue
        for field in cwl[inp]:
            m = 'Please provide an input value for {}: '.format(field)
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
