"""Configura DataFolder sin regenerar los visuales. Cerrar Desktop antes de ejecutar."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def configure(folder: Path, model_path: Path) -> None:
    folder = folder.expanduser().resolve(strict=True)
    for name in ('Customers.csv', 'Segments.csv'):
        if not (folder / name).is_file():
            raise FileNotFoundError(f'Falta {name} en {folder}')
    content = json.loads(model_path.read_text(encoding='utf-8'))
    parameters = [p for p in content['model']['expressions'] if p['name'] == 'DataFolder']
    if len(parameters) != 1:
        raise ValueError('Se esperaba exactamente un parametro DataFolder.')
    old = parameters[0]['expression']
    marker = ' meta '
    if marker not in old:
        raise ValueError('El parametro no contiene los metadatos esperados.')
    escaped = folder.as_posix().replace('#', '#(#)').replace('"', '""')
    parameters[0]['expression'] = '"' + escaped + '"' + marker + old.split(marker, 1)[1]
    model_path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--folder', required=True, type=Path, help='Carpeta que contiene Customers.csv y Segments.csv.')
    args = parser.parse_args()
    model = ROOT / 'powerbi/TelcoRetention.SemanticModel/model.bim'
    configure(args.folder, model)
    print('DataFolder configurado. Abre el PBIP y actualiza en Power BI Desktop.')


if __name__ == '__main__':
    main()
