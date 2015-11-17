from __future__ import unicode_literals
from django import template
from django.utils.translation import gettext_lazy as _
import re


class AssignNode(template.Node):

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def render(self, context):
        context[self.name] = self.value.resolve(context, True)
        return ''


def do_assign(parser, token):
    """
    Assign an expression to a variable in the current context.

    Syntax::
        {% assign [name] [value] %}
    Example::
        {% assign list entry.get_related %}
    """
    bits = token.contents.split()
    if len(bits) != 3:
        raise template.TemplateSyntaxError(
            "'%s' tag takes two arguments" % bits[0])
    value = parser.compile_filter(bits[2])
    return AssignNode(bits[1], value)

register = template.Library()
register.tag('assign', do_assign)


class ExprNode(template.Node):

    def __init__(self, expr_string, var_name):
        self.expr_string = expr_string
        self.var_name = var_name

    def render(self, context):
        try:
            clist = list(context)
            clist.reverse()
            d = {}
            d['_'] = _
            for c in clist:
                d.update(c)
            if self.var_name:
                context[self.var_name] = eval(self.expr_string, d)
                return ''
            else:
                return str(eval(self.expr_string, d))
        except:
            raise

r_expr = re.compile(r'(.*?)\s+as\s+(\w+)', re.DOTALL)


def do_expr(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires arguments" % token.contents[0])
    m = r_expr.search(arg)
    if m:
        expr_string, var_name = m.groups()
    else:
        if not arg:
            raise template.TemplateSyntaxError(
                "%r tag at least require one argument" % tag_name)

        expr_string, var_name = arg, None
    return ExprNode(expr_string, var_name)

do_expr = register.tag('expr', do_expr)
