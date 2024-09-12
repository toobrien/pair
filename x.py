import  numpy                   as      np
import  plotly.graph_objects    as      go
from    sys                     import  argv
from    time                    import  time
from    util                    import  parse_args


# python x.py rty_emd - RTY:1 EMD:1 06-14 0


def run(args: dict):

    pass


if __name__ == "__main__":

    t0   = time()
    args = parse_args(argv)
    
    modes = {
        0: run
    }

    modes[args['mode']](args)

    print(f"{time() - t0:0.1f}s")