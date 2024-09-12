import  numpy                   as      np
import  plotly.graph_objects    as      go
from    sys                     import  argv
from    time                    import  time
from    typing                  import  List
from    util                    import  parse_args, reformat


# python x.py rty_emd - RTY:1 EMD:1 06-14 0


def run(data: List[dict]):

    pass


if __name__ == "__main__":

    t0      = time()
    args    = parse_args(argv)
    x_args  = ( args['x_sym'], args['x_mult'] )
    y_args  = ( args['y_sym'], args['y_mult'] )
    data    = reformat(x_args, y_args, args['dfs'])
    
    run(data)

    print(f"{time() - t0:0.1f}s")