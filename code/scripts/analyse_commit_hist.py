import json 
import pathlib 

import tap

import matplotlib.pyplot as pyplot 


class Args(tap.Tap):
    filename: pathlib.Path


def main(args: Args):
    with open(args.filename) as f:
        hist = json.load(f)
    
    fig, ax = pyplot.subplots()
    labels = [int(x) for x in hist]
    labels.sort()
    ax.boxplot(
        [hist[str(x)] for x in labels],
        tick_labels=[str(x + 1) if x + 1 == 1 or (x + 1) % 5 == 0 else '' for x in labels],
        flierprops={
            'marker': 'x',
            'markersize': 3,
        }
    )
    ax.set_xlabel('Commit Number')
    ax.set_ylabel('Proportion of Total Changes (%)')
    ax.set_yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    ax.set_yticklabels(['0', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100'])

    fig.tight_layout()
    fig.savefig('out.png')
    pyplot.close(fig)


if __name__ == '__main__':
    main(Args().parse_args())