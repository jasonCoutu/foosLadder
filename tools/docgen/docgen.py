"""
Used to generate VAPI docs.

Release notes
=============
1.1.0
 - new docgen.py features:
   - added ability to mark parameter as deprecated DOC_DEPRECATED, DOC_DEPRECATED_ARGS
   - added ability to mark parameter as undocumented DOC_UNDOCUMENTED_ARGS
   - requires v1.9.6 of VAPI
"""

__version__ = '1.1.0'

import re
import os
import sys
import json
import string
import logging
import datetime
import importlib
from collections import defaultdict

import vapi

DEFAULT_OUTPUT   = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'doc')
CAPS_REGEX       = re.compile(r'(?P<cap>[A-Z])')
NOT_ASCII_REGEX  = re.compile(r'[^A-Za-z0-9]')
MULTI_DASH_REGEX = re.compile(r'--+')

class SectionDocument(object):
    """
    Introspects a module for various documentation values.
    """
    DOC_SECTION_NAME  = 'DOC_SECTION_NAME'
    DOC_SECTION_ORDER = 'DOC_SECTION_ORDER'
    DOC_OMIT          = 'DOC_OMIT'

    def __init__(self, module):
        self.__module_name = module
        self.module = importlib.import_module(module)

    @property
    def module_name(self):
        return self.__module_name

    @property
    def omit(self):
        return getattr(self.module, self.DOC_OMIT, False)

    @property
    def doc_section_name(self):
        name = getattr(self.module, self.DOC_SECTION_NAME, None)
        if name:
            return name
        return ' '.join(x.capitalize() for x in self.module_name.split('_'))

    @property
    def doc_section_order(self):
        return getattr(self.module, self.DOC_SECTION_ORDER, 2**15)

    @property
    def description(self):
        if self.module.__doc__:
            return self.module.__doc__.strip()
        return ''

    def to_dict(self):
        return {
            'doc_section_name' : self.doc_section_name,
            'description'      : self.description,
        }

    def __cmp__(self, other):
        if self.doc_section_order == other.doc_section_order:
            return cmp(self.doc_section_name, other.doc_section_name)
        if self.doc_section_order < other.doc_section_order:
            return -1
        return 1

class EndPointDocument(object):
    """
    Introspects a handler class for various documentation values.
    """
    DOC_NAME               = 'DOC_NAME'
    DOC_ORDER              = 'DOC_ORDER'
    URL                    = 'URL'
    DOC_OMIT               = 'DOC_OMIT'
    DOC_ARG_NOTES          = 'DOC_ARG_NOTES'
    REQUIRES_HTTPS         = 'REQUIRES_HTTPS'
    REQUIRED_ARGS          = 'REQUIRED_ARGS'
    ALLOWED_ARGS           = 'ALLOWED_ARGS'
    ARG_VALIDATORS         = 'ARG_VALIDATORS'
    ALLOW_MULTIPLE_ARGS    = 'ALLOW_MULTIPLE_ARGS'
    ARG_VALIDATOR_PREFIX   = 'validate_arg_'
    ALLOWED_METHODS        = 'ALLOWED_METHODS'
    DEFAULT_VALUES         = 'DEFAULT_VALUES'
    DOC_RESPONSE_PREFIX    = 'doc_response_'
    DOC_STATUS_CODES       = 'doc_status_codes'
    RATE_LIMIT             = 'RATE_LIMIT'
    RATE_LIMIT_GROUP       = 'RATE_LIMIT_GROUP'
    DOC_DEPRECATED         = 'DOC_DEPRECATED'
    DOC_DEPRECATED_ARGS    = 'DOC_DEPRECATED_ARGS'
    DOC_UNDOCUMENTED_ARGS  = 'DOC_UNDOCUMENTED_ARGS'

    DEFAULT_URL      = '<url not set>'
    DEFAULT_HOSTNAME = '[hostname]'

    def __init__(self, handler_class, hostname=None):
        self.handler_class = handler_class
        self.hostname      = hostname

    @property
    def module_name(self):
        return self.handler_class.__module__

    @property
    def version(self):
        return self.handler_class.VERSION

    @property
    def major_version(self):
        return self.version.split('.')[0]

    @property
    def doc_name(self):
        name = getattr(self.handler_class, self.DOC_NAME, None)
        if name:
            return name
        return CAPS_REGEX.sub(r' \g<cap>', self.handler_class.__name__).strip()

    @property
    def doc_order(self):
        return getattr(self.handler_class, self.DOC_ORDER, 2**15)

    @property
    def description(self):
        if self.handler_class.__doc__:
            return self.handler_class.__doc__.strip()
        return ''

    @property
    def url(self):
        path = getattr(self.handler_class, self.URL, self.DEFAULT_URL)
        hostname = self.hostname or self.DEFAULT_HOSTNAME
        scheme   = 'http[s]://'
        if self.handler_class.REQUIRES_HTTPS:
            scheme = 'https://'
        return scheme + hostname + path

    @property
    def omit(self):
        return getattr(self.handler_class, self.DOC_OMIT, False)

    @property
    def required_args(self):
        args = getattr(self.handler_class, self.REQUIRED_ARGS, [])
        if isinstance(args, (set, frozenset)):
            return sorted(args)
        return args

    @property
    def allowed_args(self):
        args = getattr(self.handler_class, self.ALLOWED_ARGS, [])
        if isinstance(args, (set, frozenset)):
            return sorted(args)
        return args

    @property
    def arg_validators(self):
        return getattr(self.handler_class, self.ARG_VALIDATORS, {})

    @property
    def allow_multiple_args(self):
        return getattr(self.handler_class, self.ALLOW_MULTIPLE_ARGS, [])

    @property
    def allowed_methods(self):
        return getattr(self.handler_class, self.ALLOWED_METHODS)

    @property
    def doc_arg_notes(self):
        return getattr(self.handler_class, self.DOC_ARG_NOTES, {})

    @property
    def deprecation_arg_notes(self):
        return getattr(self.handler_class, self.DOC_DEPRECATED_ARGS, {})

    @property
    def is_deprecated(self):
        deprecated = self.deprecation_note
        return deprecated is not None and deprecated != ''

    @property
    def deprecation_note(self):
        return getattr(self.handler_class, self.DOC_DEPRECATED, None)

    @property
    def get_undocumented_args(self):
        return getattr(self.handler_class, self.DOC_UNDOCUMENTED_ARGS, [])

    @property
    def rate_limits(self):
        limits = getattr(self.handler_class, self.RATE_LIMIT, [])
        if not isinstance(limits, (list, tuple)):
            limits = [limits]
        return limits

    @property
    def rate_limit_group(self):
        return getattr(self.handler_class, self.RATE_LIMIT_GROUP, None)

    def format_rate_limit(self, limit):
        period = limit[-1]
        rate   = int(limit[:-1])
        if period == 'd':
            period = '/day'
        elif period == 'h':
            period = '/hour'
        elif period == 'm':
            period = '/minute'
        return "{:,}".format(rate) + period

    def is_undocumented(self, arg):
        return arg in self.get_undocumented_args

    def get_arg_validator_description(self, arg):
        if hasattr(self.handler_class, self.ARG_VALIDATOR_PREFIX + arg):
            content = getattr(self.handler_class, self.ARG_VALIDATOR_PREFIX + arg).__doc__
            if content:
                return content.strip()
        return ''

    def get_arg_default_value(self, arg):
        default_values = getattr(self.handler_class, self.DEFAULT_VALUES, {})
        return default_values.get(arg, None)

    def get_doc_responses(self):
        attrs = []
        for item in dir(self.handler_class):
            if item.startswith(self.DOC_RESPONSE_PREFIX):
                attrs.append(item)
        attrs.sort()
        return attrs

    def get_doc_response_content(self, attr, html=True):
        content = getattr(self.handler_class, attr)()
        if isinstance(content, str):
            return content.strip()
        data = json.dumps(self.handler_class.serialize_datatypes(content), indent=4, sort_keys=True)
        if html:
            data = re.sub(r'("[^"]+"):', r'<strong>\1</strong>:', data)
        return data

    def get_doc_response_description(self, attr):
        content = getattr(self.handler_class, attr).__doc__
        if content:
            return content.strip()
        return ''

    def get_doc_status_codes(self):
        fn = getattr(self.handler_class, self.DOC_STATUS_CODES, None)
        if fn:
            return fn()
        return {}

    def get_doc_status_codes_description(self):
        fn = getattr(self.handler_class, self.DOC_STATUS_CODES, None)
        if fn:
            content = fn.__doc__
            if content:
                return content.strip()
        return ''

    def get_arg_datatype(self, arg):
        if arg.endswith('DateTime'):
            return 'datetime'
        if arg.endswith('Date'):
            return 'date'
        if arg.endswith('Time'):
            return 'time'
        if arg.endswith('Flag'):
            return 'boolean'
        validator = self.arg_validators.get(arg, None)
        if validator == int:
            return 'integer'
        if validator == float:
            return 'float'
        if validator == bool:
            return 'boolean'
        return 'string'

    def get_arg_note(self, arg):
        return self.doc_arg_notes.get(arg, '')

    def get_arg_deprecation_note(self, arg):
        return self.deprecation_arg_notes.get(arg, '')

    def supports_paged_results(self):
        return issubclass(self.handler_class, vapi.PagedApiHandler)

    def supports_total_results(self):
        return issubclass(self.handler_class, vapi.SearchApiPagedApiHandler)

    def __cmp__(self, other):
        if self.doc_order == other.doc_order:
            return cmp(self.doc_name, other.doc_name)
        if self.doc_order < other.doc_order:
            return -1
        return 1

def import_modules(modules):
    for module in modules:
        __import__(module)

def descendents(klass):
    subclasses = set()
    work = [klass]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return subclasses

def get_end_point_documents(hostname=None):
    docs = []
    for subclass in descendents(vapi.ApiHandler):
        if subclass.__module__.startswith('vapi.'):
            continue
        message = 'Importing %s.%s' % (subclass.__module__, subclass.__name__)
        doc = EndPointDocument(subclass, hostname=hostname)
        docs.append(doc)
        logging.debug('%s, done.', message)
    return docs

def get_section_documents(modules):
    docs = []
    for module in modules:
        doc = SectionDocument(module)
        docs.append(doc)
        logging.debug('Importing section information for %s.', module)
    return docs

class Generator(object):
    def __init__(self, title=None):
        self.title = title or ''

    def generate(self, section_docs, end_point_docs, output_dir=DEFAULT_OUTPUT):
        raise NotImplementedError()

class HtmlGenerator(Generator):

    BOILERPLATE_DESCRIPTION = """
All API end-points require the following GET parameters:

<table class="table table-condensed">
  <thead>
  <tr>
    <th>Parameter</th>
    <th>Required?</th>
    <th>Type</th>
    <th>Multiples?</th>
    <th>Notes</th>
  </tr>
  </thead>
  <tbody>
  <tr>
    <td><code>apiUser</code></td>
    <td class="check"><i class="icon-ok"></i></td>
    <td><code>string</code></td>
    <td></td>
    <td><small>Provided by VendAsta</small></td>
  </tr>
  <tr>
    <td><code>apiKey</code></td>
    <td class="check"><i class="icon-ok"></i></td>
    <td><code>string</code></td>
    <td></td>
    <td><small>Provided by VendAsta</small></td>
  </tr>
  </tbody>
</table>

All API responses will be a JSON dictionary of the form:
<pre>
{
    <strong>"statusCode"</strong>: 200,
    <strong>"responseTime</strong>: 13.12,
    <strong>"version"</strong>: "1.1",
    <strong>"message"</strong>: "A message may optionally appear",
    <strong>"data"</strong>: {} # may be a simple value, or a list, or a dictionary
}
</pre>
The API responses below indicate the <code>data</code> portion of the response.

Where multiple arguments are allowed, use multiple parameter names. E.g., <code>foo=1&foo=2&foo=3</code>.

<span class="label label-info">Note</span> Certain data types require particular serialized forms:
<ul>
    <li><code>datetime</code> has the form <code>2012-12-13T14:32:41Z</code></li>
    <li><code>date</code> has the form <code>2012-12-13</code></li>
    <li><code>time</code> has the form <code>14:32:41Z</code></li>
    <li><code>boolean</code> has the form<code>true</code> or <code>false</code></li>
</ul>

<hr class="bs-docs-separator"/>
<h4>Paged results</h4>

For API end-points denoted as "supports paged results", the response dictionary will have more information:
<pre>
{
    "statusCode": 200,
    ...,
    "data": [], # will be a list of results
    <strong>"nextUrl": "https://[absolute-url-to-retrieve-next-page-of-results]"</strong>,
    <strong>"totalResults": 213</strong> # this is only supported by some paged results end-points
}
</pre>
The <code>nextUrl</code> can be used to get the next page of results for the result set.
If there are no more results, this value will be <code>null</code>.

<span class="label label-important">Important</span> You must append your
<code>apiUser</code> and <code>apiKey</code> to the <code>nextUrl</code> before submitting the request.

<hr class="bs-docs-separator"/>
<h4>Response codes</h4>
<p>
Unless otherwise noted, a 200 response code indicates success and a 500 response code indicates a
server error. In general, 200-series responses are used to indicate success, 400-series responses
are used to indicate client errors, and 500-series responses are used to indicate server errors.
400-series errors often contain a message with a description of the client error.
</p>


"""

    def urlize(self, s):
        s = NOT_ASCII_REGEX.sub('-', s)
        s = MULTI_DASH_REGEX.sub('-', s)
        s = s.lower()
        s = s.strip('-')
        return s

    def format_allowed_methods(self, allowed_methods):
        return '/'.join(allowed_methods)

    def p_ize_text(self, text):
        """
        Surrounds text with paragraph tags, using blank lines to create more <p> tags.
        """
        if not text:
            return ''
        lines = text.split('\n')
        result = []
        for line in lines:
            if line.strip() == '':
                result.append('</p><p>')
            else:
                result.append(line)
        return '<p>%s</p>' % '\n'.join(result)

    def generate_arg_row(self, end_point_doc, arg, required=True):
        """
        Prints a single row. Return True if row was printed, false otherwise.
        """
        if end_point_doc.is_undocumented(arg):
            return False

        print """
    <tr>
      <td><code>%s</code></td>
""" % arg
        if required:
            print """
      <td class="check"><i class="icon-ok"></i></td>
"""
        else:
            print """
      <td></td>
"""
        print """
      <td><code>%s</code></td>
""" % end_point_doc.get_arg_datatype(arg)

        if arg in end_point_doc.allow_multiple_args:
            print """
      <td class="check"><i class="icon-ok"></i></td>
"""
        else:
            print """
      <td></td>
"""

        print """
      <td><small>%s %s %s %s</small></td>
    </tr>
""" % (
       end_point_doc.get_arg_note(arg),
       end_point_doc.get_arg_validator_description(arg),
       end_point_doc.get_arg_default_value(arg) is not None and 'Default: <code>%s</code>.' % end_point_doc.get_arg_default_value(arg) or '',
       end_point_doc.get_arg_deprecation_note(arg) and '<div class="well warning"><strong>DEPRECATED:</strong> %s</div>' % end_point_doc.get_arg_deprecation_note(arg) or '',
      )

        return True


    def generate(self, section_docs, end_point_docs):

        # TODO different doc for each version
        section_docs.sort()
        end_point_docs.sort()

        print """
<!DOCTYPE html>
<html>
<head>
  <title>%s</title>
  <link href="http://netdna.bootstrapcdn.com/twitter-bootstrap/2.1.1/css/bootstrap.min.css" rel="stylesheet"/>
  <style type="text/css">
    body {
        padding-top: 60px;
        padding-bottom: 40px;
    }
    .sidebar-nav {
        padding: 9px 0;
    }
    td.check {
        padding-left: 30px;
    }
    .dl-horizontal dt {
        width: 60px;
    }
    .dl-horizontal dd {
        margin-left: 80px;
    }
    .well.warning {
        background: #c09853;
        color: black;
    }
</style>
</head>
<body>

<div class="navbar navbar-inverse navbar-fixed-top">
  <div class="navbar-inner">
    <div class="container-fluid">
      <a class="brand" href="#">%s</a>
      <img class="pull-right" src='http://www.vendasta.com/__v45/static/images/logo-white.png'/>
    </div>
  </div>
</div>

<div class="container-fluid">
<div class="row-fluid">
<div class="span3">
<div class="well sidebar-nav">
<ul class="nav nav-list">
""" % (self.title, self.title)

        for section_doc in section_docs:
            if section_doc.omit:
                continue
            print """
  <li class="nav-header"><a href="#%s">%s</a></li>
""" % (self.urlize(section_doc.doc_section_name), section_doc.doc_section_name)

            for end_point_doc in end_point_docs:
                if end_point_doc.omit:
                    continue
                if end_point_doc.module_name != section_doc.module_name:
                    continue
                print """
      <li class="offset1"><a href="#%s-%s">%s</a></li>
""" % (self.urlize(section_doc.doc_section_name), self.urlize(end_point_doc.doc_name), end_point_doc.doc_name)

        print """
</ul>
</div>
</div>

<div class="span9">
<a id="overview"></a><h3>Overview</h3>
<div class="offset1">
%s
</div>
""" % self.p_ize_text(self.BOILERPLATE_DESCRIPTION)

        for section_doc in section_docs:
            if section_doc.omit:
                continue
            print """
<a id="%s"></a><hr class="bs-docs-separator">
<h3>%s</h3>
""" % (self.urlize(section_doc.doc_section_name), section_doc.doc_section_name)

            if section_doc.description:
                print """
%s
<div class="offset1">
""" % self.p_ize_text(section_doc.description)

            for end_point_doc in end_point_docs:
                if end_point_doc.omit:
                    continue
                if end_point_doc.module_name != section_doc.module_name:
                    continue
                print """
  <a id="%s-%s"></a><hr class="bs-docs-separator"/>
  <h4>%s <small class="pull-right">v%s
""" % (self.urlize(section_doc.doc_section_name),
       self.urlize(end_point_doc.doc_name),
       end_point_doc.doc_name,
       end_point_doc.version)

                rate_limits = end_point_doc.rate_limits
                if rate_limits:
                    print """
  &nbsp;&nbsp;&nbsp;Rate limit%s:
""" % (len(rate_limits) > 1 and 's' or '')
                    limit_count = 0
                    for limit in rate_limits:
                        limit_count += 1
                        print """
    %s%s
""" % (end_point_doc.format_rate_limit(limit), (limit_count < len(rate_limits) and ',' or ''))
                    if end_point_doc.rate_limit_group:
                        print """
    (limit group: '%s')
""" % end_point_doc.rate_limit_group

                print """
  </small></h4>
"""

                print """
  <pre><strong>%s %s</strong></pre>
""" % (self.format_allowed_methods(end_point_doc.allowed_methods), end_point_doc.url)

                if end_point_doc.supports_paged_results() or end_point_doc.supports_total_results():
                    print """
  <div class='pull-right'>
"""
                if end_point_doc.supports_paged_results():
                    print """
    <div><small><em>* supports paged results <code>nextUrl</code></em></small></div>
"""
                if end_point_doc.supports_total_results():
                    print """
    <div><small><em>* supports <code>totalResults</code></em></small></div>
"""
                if end_point_doc.supports_paged_results() or end_point_doc.supports_total_results():
                    print """
  </div>
"""
                if end_point_doc.is_deprecated:
                    print """
  <div class='clearfix well warning'>
  %s
  </div>
""" % self.p_ize_text('<strong>DEPRECATED:</strong> ' + end_point_doc.deprecation_note)

                if end_point_doc.description:
                    print """
  <div class='clearfix'>
  %s
  </div>
""" % self.p_ize_text(end_point_doc.description)

                ### PRINT Parameters section
                print """
  <div class='clearfix'>
  <table class="table table-condensed">
  <thead>
  <tr>
    <th>Parameter</th>
    <th>Required?</th>
    <th>Type</th>
    <th>Multiples?</th>
    <th>Notes</th>
  </tr>
  </thead>
  <tbody>
"""
                num_args = 0
                for arg in end_point_doc.required_args:
                    result = self.generate_arg_row(end_point_doc, arg, required=True)
                    if result:
                        num_args += 1
                for arg in end_point_doc.allowed_args:
                    result = self.generate_arg_row(end_point_doc, arg, required=False)
                    if result:
                        num_args += 1
                if num_args == 0:
                    print """
    <tr>
        <td colspan="3"><em>None</em></td>
    </tr>
"""
                if end_point_doc.supports_paged_results():
                    print """
    <tr>
      <td><code>pageSize</code></td>
      <td></td>
      <td><code>int</code></td>
      <td></td>
      <td><small>Must be a positive integer.</small></td>
    </tr>
"""
                print """
  </tbody>
  </table>
  </div>
"""
                ### end Parameters section

                status_codes = end_point_doc.get_doc_status_codes()
                if status_codes:
                    print """
  <h6>Response codes</h6>
  %s
  <dl class="dl-horizontal">
""" % self.p_ize_text(end_point_doc.get_doc_status_codes_description())
                    for key in sorted(status_codes.keys()):
                        print """
    <dt>%s</dt><dd>%s</dd>
""" % (key, status_codes[key])
                    print """
  </dl>
"""

                responses = end_point_doc.get_doc_responses()
                multiple_responses = len(responses) > 1
                for index, response in enumerate(responses):
                    print """
  <h6>Example response%s</h6>
  %s
  <pre class="pre-scrollable"><small>%s</small></pre>
""" % (multiple_responses and (' %d' % (index + 1)) or '',
       self.p_ize_text(end_point_doc.get_doc_response_description(response)),
       end_point_doc.get_doc_response_content(response))

            print """
</div>
"""

        print """
</div>
</div>
<hr>
<footer>
  <p class="pull-right"><small>Copyright &copy;%d VendAsta Technologies Inc.</small></p>
</footer>
</div>
</body>
</html>
""" % datetime.datetime.utcnow().year


def main():
    if len(sys.argv) == 1:
        print >> sys.stderr, """
Usage: docgen.py [document title] [api-hostname, e.g., repcore-prod.appspot.com] [comma-separated module list]
"""
        sys.exit(1)

    title = sys.argv[1]
    hostname = sys.argv[2]
    modules = sys.argv[3].split(',')
    # modules = ['foo_bar', 'zzz']
    # hostname = 'repcore-prod.appspot.com'
    logging.getLogger().setLevel(logging.DEBUG)
    import_modules(modules)
    end_point_docs = get_end_point_documents(hostname=hostname)
    section_docs   = get_section_documents(modules)
    generator = HtmlGenerator(title=title)
    generator.generate(section_docs, end_point_docs)

if __name__ == '__main__':
    main()
