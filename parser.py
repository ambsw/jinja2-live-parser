# -*- coding: utf-8 -*-
import json
from pprint import pprint
from lxml import etree
from lxml.etree import XMLSyntaxError

from flask import Flask, render_template, request
from jinja2 import Environment, meta, TemplateSyntaxError, StrictUndefined, UndefinedError

# For dynamic loading of filters
import imp
from inspect import getmembers, isfunction
import os

app = Flask(__name__)

# Load filters in filters dir
filter_path = 'filters'
filter_files = []
added_filters = {}

# Find py files and turn then into filterpath/blah/filter.py
for e in os.walk(filter_path, followlinks=True):
    for f in e[2]:
        if f.endswith('py'):
            print("Adding %s" % os.path.join(e[0], f))
            filter_files.append(os.path.join(e[0], f))

for filter in filter_files:
    mod_name, file_ext = os.path.splitext(os.path.split(filter)[-1])
    py_mod = imp.load_source(mod_name, filter)
    for name, function in getmembers(py_mod):
        if isfunction(function) and not name.startswith('_'):
            # Saving filter info to put it in HTML at some point
            added_filters[name] = function.__doc__
            # add filter to jinja
            app.jinja_env.filters[name] = function


# These are the added filters.  must add these name + doc strings to the html
# Also do this for built-in jinja filters
# for f in sorted(added_filters):
#    print("%s: %s" % (f, added_filters[f]))

@app.route("/")
def hello():
    return render_template('index.html',
                           all_filters=app.jinja_env.filters
                           )


@app.route('/convert', methods=['GET', 'POST'])
def convert():
    # Verify that macros section compiles
    try:
        if int(request.form['strictformat']):
            app.jinja_env.undefined = StrictUndefined
        # tpl = app.jinja_env.from_string(request.form['template'])
        tpl = app.jinja_env.from_string(request.form['macros'])
    except TemplateSyntaxError as err:
        response = {'macros-error': "ERROR: " + err.message}
        return json.dumps(response)
    # Verify that macros plus template compile correctly
    try:
        if int(request.form['strictformat']):
            app.jinja_env.undefined = StrictUndefined
        # tpl = app.jinja_env.from_string(request.form['template'])
        tpl = app.jinja_env.from_string(request.form['macros'] + "\n" + request.form['template'])
    except TemplateSyntaxError as err:
        response = {'template-error': "ERROR: " + err.message}
        return json.dumps(response)

    response = {}

    try:
        values = json.loads(request.form['values'])
        formatted = tpl.render(values)
    except ValueError as err:
        # Invalid JSON
        response['values-error'] = "ERROR: " + err.message
        return json.dumps(response)
    except UndefinedError as err:
        # Variable not present in template
        response['macros-error'] = "ERROR: " + err.message
        response['template-error'] = "ERROR: " + err.message
        return json.dumps(response)

    pprint(formatted)
    if int(request.form['xmlformat']):
        try:
            parser = etree.XMLParser(remove_blank_text=True)
            elem = etree.XML(formatted, parser=parser)
            formatted = etree.tostring(elem, pretty_print=True)
        except XMLSyntaxError as err:
            # Template output was not valid XML
            response['render-error'] = "ERROR: Output was not valid XML "

    response['render'] = formatted
    return json.dumps(response)


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
