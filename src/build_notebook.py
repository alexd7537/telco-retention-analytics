"""Convierte el archivo educativo por celdas a ipynb y ejecuta sus celdas en Python.
No requiere instalar Jupyter para generar salidas reproducibles de texto.
"""
from pathlib import Path
import contextlib
import io
import json
import os
import uuid

ROOT=Path(__file__).resolve().parents[1]

def main():
    source=(ROOT/'notebooks/01_exploracion.py').read_text(encoding='utf-8')
    chunks=[]; kind=None; lines=[]
    for line in source.splitlines(keepends=True):
        if line.startswith('# %%'):
            if kind: chunks.append((kind,lines))
            kind='markdown' if '[markdown]' in line else 'code'; lines=[]
        else: lines.append(line)
    if kind:chunks.append((kind,lines))
    cells=[]; scope={}; count=0; previous=Path.cwd()
    try:
        os.chdir(ROOT)
        for index,(kind,lines) in enumerate(chunks):
            text=''.join(lines)
            if kind=='markdown': text=''.join(line[2:] if line.startswith('# ') else line[1:] if line.startswith('#') else line for line in lines)
            cell={'cell_type':kind,'id':uuid.uuid5(uuid.NAMESPACE_URL,'telco-notebook/'+str(index)).hex[:12],'metadata':{},'source':text.splitlines(keepends=True)}
            if kind=='code':
                count+=1; out=io.StringIO()
                with contextlib.redirect_stdout(out): exec(compile(text,f'notebook-cell-{count}','exec'),scope)
                cell.update(execution_count=count,outputs=[{'output_type':'stream','name':'stdout','text':out.getvalue().splitlines(keepends=True)}] if out.getvalue() else [])
            cells.append(cell)
    finally: os.chdir(previous)
    notebook={'cells':cells,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},
        'language_info':{'name':'python','version':__import__('platform').python_version()},
        'execution_note':'Celdas ejecutadas secuencialmente en Python local mediante build_notebook.py; no se uso un kernel Jupyter.'},'nbformat':4,'nbformat_minor':5}
    (ROOT/'notebooks/01_exploracion.ipynb').write_text(json.dumps(notebook,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Notebook: {count} celdas de codigo ejecutadas sin errores.')

if __name__=='__main__':main()
