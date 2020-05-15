import os

for pwd,dirs,files in os.walk("./mobile_portal_py3",topdown=False):
    for file in files:
        if file.endswith('.py') and file != '__init__.py':
            exec("import " + pwd[2:].replace('/','.') + "." + file[:-3])