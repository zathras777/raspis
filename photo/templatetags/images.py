from django import template
from django.utils.safestring import mark_safe
from django.template import Template

from photo.models import *

register = template.Library()

IMG_TAG=Template("""
  <img data-id="{{image.photo.id}}" src="{{ image.img.url }}"
       width="{{image.img.width}}" height="{{image.img.height}}"
       alt="{{image.photo.title|default:"Untitled"}}"
       title="{{image.photo.title|default:"Untitled"}}"
       />
""")

class imageTagNode(template.Node):
    def __init__(self, node, format_string):
        self.node_var = template.Variable(node)
        if '.' in format_string:
            self.format_node = template.Variable(format_string)
        else:
            self.format = format_string.replace("'", "").replace("\"", "").strip()

    def render(self, context):
        pic = self.node_var.resolve(context)
        if not pic:
            return ""
        if hasattr(self, 'format_node'):
            self.format = self.format_node.resolve(context)
        print(pic)
        if isinstance(pic, Thumbnail):
            img = pic
        else:
            img = pic.get_thumbnail(self.format)

        if not img:
            return ""
        context.push()
        context['image'] = img
        context['pic'] = pic
        output = IMG_TAG.render(context)
        context.pop()
        return mark_safe(output)

@register.tag
def getImageTag(parser, token):
    contents = token.split_contents()
    if len(contents) < 2:
        raise template.TemplateSyntaxError("%r tag requires at least one argument" % contents[0])
    return imageTagNode(contents[1], contents[2] if len(contents) == 3 else '')
