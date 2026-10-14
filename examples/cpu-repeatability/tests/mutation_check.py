"""Optional stdlib mutation experiment: temporary checker copies only."""
import ast,copy,json,os,subprocess,tempfile,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]; tool=root/'tools/check_repeat.py'; tree=ast.parse(tool.read_text())
calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='_require']
rows=[]
for call in sorted(calls,key=lambda n:n.lineno):
    class Remove(ast.NodeTransformer):
        def visit_Call(self,node):
            if getattr(node,'lineno',None)==call.lineno and isinstance(node.func,ast.Name) and node.func.id=='_require':
                return ast.copy_location(ast.Constant(None),node)
            return self.generic_visit(node)
    modified=Remove().visit(copy.deepcopy(tree)); ast.fix_missing_locations(modified)
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/'checker.py';path.write_text(ast.unparse(modified))
        result=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(root/'tests'),'-p','test_check_repeat.py'],cwd=root,env={**os.environ,'CHECKER_PATH':str(path)},capture_output=True,text=True)
    rows.append({'line':call.lineno,'reason':ast.unparse(call.args[1]),'killed':result.returncode!=0})
print(json.dumps(rows,indent=2)); print('killed',sum(r['killed'] for r in rows),'/',len(rows))
if not all(r['killed'] for r in rows):raise SystemExit(1)
