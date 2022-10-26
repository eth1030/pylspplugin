import ast


# function
def get_functions(path):
    """ 
    Using ast from standard python libaries to find all the functions that are used in the current code 
    cell (put in to the function through the plugin)
    """
    results = []
    root = ast.parse(path.read())
    for node in ast.iter_child_nodes(root):

    # for node in ast.walk(ast.parse(inspect.getsource(path))):
        # try:
        #     is_print = (node.id == 'execute')
        # except AttributeError:  # only expect id to exist for Name objs
        #     pass
        # if is_print:
        #     fun = []



        if isinstance(node, ast.Expr):
            fun = node.value
        else:
            continue
        
        lineno = node.lineno
        col_offset = node.col_offset
        end_col_offset = node.end_col_offset
        
        for e in node.value:
            results.append([fun, e.Call, lineno, col_offset, end_col_offset])
        print(results)
    return results 