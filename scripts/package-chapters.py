"""Source-only submission archives. Does not invent screenshots or run evidence."""
from pathlib import Path
import json,zipfile
root=Path(__file__).resolve().parents[1]
output=root/'submissions'/'chapters';output.mkdir(parents=True,exist_ok=True)
for number in [1,2,4,5,6,8]:
    chapter=f'ch{number:02}'
    with zipfile.ZipFile(output/(chapter+'.zip'),'w',zipfile.ZIP_DEFLATED) as archive:
        for folder in ['labs','infra','scripts','data','app','docs']:
            for path in (root/folder).rglob('*'):
                if not path.is_file() or '__pycache__' in path.parts or path.name=='public-threats.json':continue
                archive.write(path,path.relative_to(root))
        for name in ['README.md','STATUS.md','compose.yaml','Dockerfile','requirements.txt','requirements-labs.txt','Dockerfile.labs','LICENSE','ATTRIBUTION.md','.env.example','.gitattributes']:
            archive.write(root/name,name)
        for folder in sorted((root/'labs'/chapter).glob('activity_*')):
            for path in folder.iterdir():
                if not path.is_file():continue
                content=path.read_text()
                if path.name=='run.py':content=content.replace('parents[3]','parents[1]')
                archive.writestr(folder.name+'/'+path.name,content)
        archive.writestr('SUBMISSION-STATUS.md',f'# DRAFT — {chapter}\n\nRunnable source supplied. Live outputs and real screenshot/script-listing DOCX remain pending runtime execution. Activity folders include shared prerequisites. Missing faculty definitions remain gaps; see labs/README.md.\n')
with zipfile.ZipFile(output/'ch07-project.zip','w',zipfile.ZIP_DEFLATED) as archive:
    for folder in ['app','data','labs','scripts','infra','docs']:
        for path in (root/folder).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts and path.name!='public-threats.json':archive.write(path,path.relative_to(root))
    for name in ['README.md','requirements.txt','requirements-labs.txt','Dockerfile','Dockerfile.labs','compose.yaml','LICENSE','ATTRIBUTION.md','STATUS.md','.env.example','.gitattributes']:
        archive.write(root/name,name)
print(output)
