"""Regenera entregables derivados. Cerrar Power BI y respaldar ediciones manuales primero."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-powerbi',action='store_true',help='Preserva cambios manuales del informe Power BI.')
    args=parser.parse_args()
    files=['analyze.py','build_notebook.py','build_report.py']
    if not args.skip_powerbi:files.append('build_powerbi.py')
    for filename in files:
        subprocess.run([sys.executable,str(ROOT/'src'/filename)],cwd=ROOT,check=True)
    subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,check=True)

if __name__=='__main__':main()
