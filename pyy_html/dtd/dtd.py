VALID    = 'valid'
REQUIRED = 'required'
CHILDREN = 'children'
DEFAULT  = 'default'
CUSTOM   = 'custom'
 
from pyy_html.html import html_tag, comment

class dtdmeta(type):
  def __init__(cls, name, bases, dictx):
    super(dtdmeta, cls).__init__(name, bases, dictx)
    for tag, dict in cls.valid.iteritems():
      dict.setdefault(VALID,    set([]))
      dict.setdefault(REQUIRED, set([]))
      dict.setdefault(CHILDREN, set([]))
      dict.setdefault(DEFAULT,  {})

class dtd(object):
  __metaclass__ = dtdmeta
  
  valid = {}
   
  @classmethod
  def validate(self, tag, child=None):
    cls   = type(tag)
    valid = self.valid[cls]
    

    #Check children
    children = child and [child] or tag.children
    if tag.is_single and children:
      raise ValueError('%s element cannot contain any child elements. Currently has: %s.' \
        % (cls.__name__, ', '.join(type(c).__name__ for c in children)))
    
    for child in children:
      if not isinstance(child, html_tag): continue    # utility or user-derived class. leave it alone
      if type(child) not in valid[CHILDREN]:
        raise ValueError('%s element cannot contain %s element as child.' \
          % (cls.__name__, type(child).__name__))
      
      #Recurse validation to child tag
      if isinstance(child, html_tag) and not isinstance(child, comment):
        self.validate(child)
    
    #Add default attributes
    for attribute, value in valid[DEFAULT].iteritems():
      tag.attributes.setdefault(attribute, value)
    
    if tag.allow_invalid: # should this apply recursively to children?
      return True
    
    #Check for invalid attributes
    invalid_attributes = []
    for attribute, value in tag.attributes.iteritems():
      if attribute not in valid[VALID]: invalid_attributes.append(attribute)
    if invalid_attributes:
      raise AttributeError('%s element has one or more invalid attributes: %s.' \
        % (cls.__name__, ', '.join(invalid_attributes)))
    
    #Check for missing required attributes
    missing_attributes = [attribute for attribute in valid[REQUIRED] if attribute not in tag.attributes]
    if missing_attributes:
      raise AttributeError('%s element has one or more missing attributes that are required: %s.' \
        % (cls.__name__, ', '.join(missing_attributes)))
    
    #Check if there is a custom validation function and pass the tag to it
    if CUSTOM in valid and not valid[CUSTOM](tag):
      raise AttributeError('%s element failed custom validation check.' % (cls.__name__))
    
    return True
  
  @classmethod
  def render(self):
    return self.docstring
  __str__ = __unicode__ = render
 

