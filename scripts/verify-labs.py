"""Capture executable checks available in this environment, including blocked attempts."""
import datetime,json,subprocess,sys,os
from pathlib import Path
root=Path(__file__).resolve().parents[1]
output=root/'results'/'verification';output.mkdir(parents=True,exist_ok=True)
checks=[]
def check(name,args):
    try:
        result=subprocess.run(args,cwd=root,text=True,capture_output=True,timeout=90)
    except subprocess.TimeoutExpired:
        result=subprocess.CompletedProcess(args,124,stdout='',stderr='Verification command exceeded 90 seconds; no success claimed')
    (output/(name+'.log')).write_text(result.stdout+result.stderr)
    checks.append(dict(name=name,command=args,exit_code=result.returncode,evidence=str((output/(name+'.log')).relative_to(root))))
check('compile',[sys.executable,'-m','compileall','-q','labs','app'])
check('unit-tests',[sys.executable,'-m','unittest','discover','-s','tests','-v'])
for file in sorted((root/'infra').glob('*.yaml')):
    if file.name in ('backup.yaml','grading.yaml'):continue
    check('compose-'+file.stem,['docker','compose','-f',str(file),'config','--quiet'])
os.environ['LAB_IMAGE']='example/college-mongo-labs:validation-only'
check('compose-grading',['docker','compose','-f','infra/standalone.yaml','-f','infra/grading.yaml','config','--quiet'])
check('compose-backup',['docker','compose','-f','infra/replica.yaml','-f','infra/backup.yaml','config','--quiet'])
for file in list((root/'scripts').glob('*.sh'))+list((root/'infra').glob('*.sh')):
    check('shell-'+file.stem,['bash','-n',str(file)])
for i in range(1,19):check(f'ch{i:02}-attempt',[sys.executable,'-m','labs.run',f'ch{i:02}','--mode','quick'])
check('docker-runtime',['docker','version'])
(output/'checks.json').write_text(json.dumps(dict(timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=checks),indent=2))
for row in checks:print(row['name'],row['exit_code'])
