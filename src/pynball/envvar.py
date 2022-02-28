# Core Library modules
import ast
import os

new_name = "3.10"
match = {}

path = os.environ["PATH"]
print(type(path))

versions_var = (
    r"{'3.8':'D:\PYTHON\python3.8',"
    r"'3.9':'D:\PYTHON\python3.9',"
    r"'3.10':'D:\PYTHON\python3.10'}"
)
versions = ast.literal_eval(versions_var)

for name in versions:
    name_path = versions[name]
    if name_path in path:
        match[name] = name_path
        print(f"True: {name_path}")

match_no = len(match)
if match_no == 1:
    # only 1 match - simply text.replace( a,b)
    path_new = path.replace(list(match.values())[0], versions[new_name])
    print(path_new)

elif match_no == 0:
    # prepend to front of path
    # path_new = versions [new_name] + old_path   # noqa
    pass

elif match_no > 1:
    # raise error - multiple python versions found in path
    pass

print(versions)
print(path)
