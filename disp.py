import  polars                  as      pl
import  plotly.graph_objects    as      go
import  numpy                   as      np
from    sys                     import  argv
from    time                    import  time
from    typing                  import  List
from    util                    import  get_dfs, parse_args, resample


pl.Config.set_tbl_cols(-1)
pl.Config.set_tbl_rows(-1)

INTERVAL = 60


# python x.py rty_emd - RTY:1 EMD:1 06-14 0


def demeaned(args: dict):

    fig = go.Figure()
    i_  = 0
    X   = []

    for date, df in args['dfs'].items():

        ts          = np.array(df["ts"])
        x           = np.array(df[args['x_sym']])
        y           = np.array(df[args['y_sym']])
        spread      = y * float(args['y_mult']) - x * float(args['x_mult'])
        demeaned    = spread - np.mean(spread)
        ts          = [ t.split("T")[1] for t in ts ]

        fig.add_trace(
            go.Scattergl(
                {
                    "x":        [ i_ + i for i in range(len(ts)) ],
                    "y":        demeaned,
                    "name":     date,
                    "text":     ts,
                    #"marker":   { "color": "#0000FF" }
                }
            )
        )

        i_ += len(ts)
        X.extend(demeaned)

    sigma = np.std(X)

    fig.add_hline(y = 0, line_color = "#FF0000")
    fig.add_hline(y = sigma, line_color = "#FF00FF")
    fig.add_hline(y = -sigma, line_color = "#FF00FF")

    fig.show()


def continuous(args: dict):

    fig         = go.Figure()
    A           = []
    T           = []
    i_          = 0

    for date, df in args['dfs'].items():

        ts          = df["ts"]
        x           = np.array(df[args['x_sym']])
        y           = np.array(df[args['y_sym']])
        spread      = y * float(args['y_mult']) - x * float(args['x_mult'])
        mu          = np.cumsum(spread) / np.array([ i for i in range(1, len(spread) + 1) ])
        spread      = resample(spread, INTERVAL)
        mu          = resample(mu, INTERVAL)
        text        = resample(ts, INTERVAL)

        fig.add_trace(
            go.Scattergl(
                {
                    "x":    [ i_ + i for i in range(len(ts)) ],
                    "y":    spread,
                    "name": date,
                    "text": text,
                }
            )
        )

        i_ = i_ + len(spread)

        A.extend(mu)
        T.extend(text)

    fig.add_trace(
        go.Scattergl(
            {
                "x":        [ i for i in range(len(A)) ],
                "y":        A,
                "name":     "mean",
                "text":     T,
                "marker":   { "color": "#FF00FF" } 
            }
        )
    )

    fig.show()


if __name__ == "__main__":

    t0   = time()
    args = parse_args(argv)

    modes = {
        0: demeaned,
        1: continuous
    }

    modes[args['mode']](args)

    print(f"{time() - t0:0.1f}s")