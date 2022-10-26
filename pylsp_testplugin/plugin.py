import os
import logging
import ast


from pylsp import hookimpl, lsp
from .detect import ASTWalker


# Setting up basic configuration, logging everything that has an ERROR level 
# Also found out through debugging that the logger that is defined here is NOT logger that prints
# to terminal when you run Jupyter Lab
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Hookimpl is from pylsp, do not touch this. Setting helps with making sure PyLsp adds this extension.
# The pylsp hooks corresponds to Language Server Protocol messages
# can be found https://microsoft.github.io/language-server-protocol/specification
# https://github.com/python-lsp/python-lsp-server/blob/develop/pylsp/hookspecs.py
@hookimpl
def pylsp_settings():
    return {
        "plugins": {
            "pylsPlugins": {
                "enabled": True,
                "recursive": False,
                "reason_keyword": "reason",
                "cache_dir": None,
                "additional_search_paths": []
            }
        }
    }

# Find this corresponding hook in documentation
@hookimpl
def pylsp_lint(config, document):
    # Define vaiables here
    funcdiagnostics = []

    # Set up settings and search paths (Using OS)
    settings = config.plugin_settings('pylsPlugins',
                                      document_path=document.path)
    search_paths = [os.path.dirname(os.path.abspath(document.path))]
    search_paths.extend(settings.get('additional_search_paths'))

    # try-except to catch any expections that rises
    try:
        with open(document.path, 'r') as code: #opens the current code in the backend for parsing
            tree = ast.parse(code)
            ast_walker = ASTWalker()
            ast_walker.visit(tree)
            importFunctions = ast_walker.candidates
            funcdiagnostics = format_sql(importFunctions, [])
    except SyntaxError as e:
        logger.error('Syntax error at {} - {} ({})', e.line, e.column, e.message)
        raise e
    return funcdiagnostics

def format_sql(importFunctions, funcdiagnostics):
    """
    Formatting the error messages that comes up this is what is returned.
    Requires the parseImport parser to return the line number of the import line
    and character
    """

    if importFunctions:
        for x in range(len(importFunctions)):
            err_range = {
                'start': {'line': importFunctions[x][2] - 1, 'character': importFunctions[x][3]},
                'end': {'line': importFunctions[x][2] - 1, 'character': importFunctions[x][4]},
            }
            funcdiagnostics.append({
                'source': 'RTQA',
                'range': err_range,
                'message': "You have used the sql function" + importFunctions[x][1] + " here.",
                'severity': lsp.DiagnosticSeverity.Information,
            })

    return funcdiagnostics

# def format_text(import_cases, diagnostics):
#     """
#     Formatting the error messages that comes up this is what is returned.
#     Requires the parseImport parser to return the line number of the import line
#     and character
#     """

#     if import_cases:
#         for x in range(len(import_cases)):
#             err_range = {
#                 'start': {'line': import_cases[x][3] - 1, 'character': import_cases[x][4]},
#                 'end': {'line': import_cases[x][3] - 1, 'character': import_cases[x][5]},
#             }
#             diagnostics.append({
#                 'source': 'RTQA',
#                 'range': err_range,
#                 'message': "You have imported " + import_cases[x][1][0] + " here.",
#                 'severity': lsp.DiagnosticSeverity.Information,
#             })

#     return diagnostics

# import logging

# from pylsp import hookimpl, uris


# logger = logging.getLogger(__name__)


# @hookimpl
# def pylsp_settings():
#     logger.info("Initializing pylsp_testplugin")

#     # Disable default plugins that conflicts with our plugin
#     return {
#         "plugins": {
#             # "autopep8_format": {"enabled": False},
#             # "definition": {"enabled": False},
#             # "flake8_lint": {"enabled": False},
#             # "folding": {"enabled": False},
#             # "highlight": {"enabled": False},
#             # "hover": {"enabled": False},
#             # "jedi_completion": {"enabled": False},
#             # "jedi_rename": {"enabled": False},
#             # "mccabe_lint": {"enabled": False},
#             # "preload_imports": {"enabled": False},
#             # "pycodestyle_lint": {"enabled": False},
#             # "pydocstyle_lint": {"enabled": False},
#             # "pyflakes_lint": {"enabled": False},
#             # "pylint_lint": {"enabled": False},
#             # "references": {"enabled": False},
#             # "rope_completion": {"enabled": False},
#             # "rope_rename": {"enabled": False},
#             # "signature": {"enabled": False},
#             # "symbols": {"enabled": False},
#             # "yapf_format": {"enabled": False},
#         },
#     }


# @hookimpl
# def pylsp_code_actions(config, workspace, document, range, context):
#     logger.info("textDocument/codeAction: %s %s %s", document, range, context)

#     return [
#         {
#             "title": "Extract method",
#             "kind": "refactor.extract",
#             "command": {
#                 "command": "example.refactor.extract",
#                 "arguments": [document.uri, range],
#             },
#         },
#     ]


# @hookimpl
# def pylsp_execute_command(config, workspace, command, arguments):
#     logger.info("workspace/executeCommand: %s %s", command, arguments)

#     if command == "example.refactor.extract":
#         current_document, range = arguments

#         workspace_edit = {
#             "changes": {
#                 current_document: [
#                     {
#                         "range": range,
#                         "newText": "replacement text",
#                     },
#                 ]
#             }
#         }

#         logger.info("applying workspace edit: %s %s", command, workspace_edit)
#         workspace.apply_edit(workspace_edit)


# @hookimpl
# def pylsp_definitions(config, workspace, document, position):
#     logger.info("textDocument/definition: %s %s", document, position)

#     filename = __file__
#     uri = uris.uri_with(document.uri, path=filename)
#     with open(filename) as f:
#         lines = f.readlines()
#         for lineno, line in enumerate(lines):
#             if "def pylsp_definitions" in line:
#                 break
#     return [
#         {
#             "uri": uri,
#             "range": {
#                 "start": {
#                     "line": lineno,
#                     "character": 4,
#                 },
#                 "end": {
#                     "line": lineno,
#                     "character": line.find(")") + 1,
#                 },
#             }
#         }
#     ]
