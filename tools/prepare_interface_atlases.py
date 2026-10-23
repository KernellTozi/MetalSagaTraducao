"""One local action to prepare preview sheets and lossless editable atlas copies."""
import argparse
from datetime import datetime
from pathlib import Path

from reinsertion import ROOT, local
from explore_interface_atlases import export as preview
from interface_atlas_pack import export as editable


def main():
    parser = argparse.ArgumentParser(description='Preparar atlas originais em PNG, sem alterar ISO')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    output = local(args.output or ROOT/'work'/('atlas-interface-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f')), True)
    preview(output/'previews')
    result = editable(output/'editaveis')
    print(f"{len(result['entries'])} texturas preparadas em {output}")
    print('Previews RGB sao apenas referencia. Editar somente PNG indexado em editaveis/.')
    print('Nenhuma ISO ou arquivo original foi alterado.')


if __name__ == '__main__':
    main()
