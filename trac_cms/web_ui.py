# -*- coding: utf-8 -*-
#
# The MIT License
# 
# Copyright (c) 2011 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
import re

try:
    import json
except ImportError:
    import simplejson as json

from genshi.filters.transform import Transformer
from genshi.output import DocType
from genshi.template import TemplateLoader
from trac.core import Component, implements
from trac.resource import Resource
from trac.web import IRequestHandler


__all__ = ['TracCMSModule', ]

# --- wiki_to_html -------------------------------------------------------------
from trac.mimeview.api import Context
from trac.wiki.formatter import HtmlFormatter

def context_for_resource(req, resource):
    context = Context(resource, href=req.href, perm=req.perm)
    # HtmlFormatter relies on the .req even though that's not always present
    # in a Context. Seems like a known dark spot in Trac's API. Check 
    # comments in trac.mimeview.api.Context.__call__()
    context.req = req
    return context

def wiki_to_html(env, context, wikitext):
    return HtmlFormatter(env, context, wikitext).generate()
# ------------------------------------------------------------------------------


class TracCMSModule(Component):
    implements(IRequestHandler)
    
    def match_request(self, req):
        # TODO: Check for dir and only match if index.html exists
        return self._matches_static_file(req) or self._matches_template(req)
    
    def process_request(self, req):
        if self._matches_static_file(req):
            req.send_file(self._static_filename(req))
    
        content_filename = self._content_filename(req)
        if os.path.isdir(content_filename):
            content_filename = os.path.join(content_filename, 'index.html')
        content = open(content_filename).read().decode('UTF-8')

        context = context_for_resource(req, Resource('cms', req.path_info))
        html = wiki_to_html(self.env, context, content)

        metadata = {}
        match = re.search('{{{\s*#!comment\s*metadata=(.*?)\s*}}}', content, re.DOTALL)
        if match:
            metadata = json.loads(match.group(1))
        
        layout_template = metadata.get('template', 'layout.html')
        output = self._render(layout_template, content=html, req=req, metadata=metadata)
        req.send(output, 'text/html')
    
    # --------------------------------------------------------------------------
    
    def _matches_template(self, req):
        content_filename = self._content_filename(req)
        if content_filename is None:
            return False
        return os.path.exists(content_filename)
    
    def _matches_static_file(self, req):
        static_filename = self._static_filename(req)
        if static_filename is None:
            return False
        return os.path.exists(static_filename) and os.path.isfile(static_filename)
    
    def _static_filename(self, req):
        return self._filename_from_req(req, 'cms', 'static')
    
    def _content_filename(self, req):
        return self._filename_from_req(req, 'cms', 'content')
    
    def _filename_from_req(self, req, *dir_names):
        # strip leading '/' from request
        request_path = req.path_info[1:]
        base_path = os.path.join(self.env.path, *dir_names)
        filename = os.path.normpath(os.path.join(base_path, request_path))
        
        # path traversal protection
        if not filename.startswith(base_path):
            return None
        return filename
    
    def _markup_stream(self, template_filename, **kwargs):
        loader = TemplateLoader([os.path.join(self.env.path, 'cms', 'templates')], variable_lookup='lenient')
        template = loader.load(template_filename)
        return template.generate(**kwargs)
    
    def _render(self, template_filename, **kwargs):
        stream = self._markup_stream(template_filename, **kwargs)
        if 'metadata' in kwargs and kwargs['metadata'].get('lang'):
            switcher_stream = self._markup_stream('language_switcher.html', **kwargs)
            available_languages = kwargs['metadata'].get('lang')
            
            transformer = Transformer('//div[@id="main"]')
            stream = stream | transformer.prepend(switcher_stream)
        
        return stream.render('xhtml', doctype=DocType.XHTML_STRICT)

# ------------------------------------------------------------------------------
    

