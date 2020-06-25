"""
Environment definition

"""


def before_scenario(context, scenario):
    """Be sure there's a place to store test scenario data"""
    context.data = {}
    context.data['disable_check'] = False
    context.data['type_env'] = []
    context.data['bindings'] = {}
    context.data['container'] = ""
