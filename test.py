import  polars                  as      pl
import  plotly.graph_objects    as      go
import  numpy                   as      np
from    sys                     import  argv
from    time                    import  time
from    typing                  import  List
from    util                    import  get_dfs, resample


pl.Config.set_tbl_cols(-1)
pl.Config.set_tbl_rows(-1)

INTERVAL = 60


# python test.py rty_emd - RTY:1 EMD:1 06-14 0


def daily_demeaned(dfs: List[pl.DataFrame]):

    fig = go.Figure()

    for date, df in dfs.items():

        ts          = np.array(df["ts"])
        x           = np.array(df[x_sym])
        y           = np.array(df[y_sym])
        spread      = y * float(y_mult) - x * float(x_mult)
        demeaned    = spread - np.mean(spread)
        ts          = [ t.split("T")[1] for t in ts ]

        fig.add_trace(
            go.Scattergl(
                {
                    "x":    ts,
                    "y":    demeaned,
                    "name": date,
                    "text": [ f"{i:0.2f}" for i in spread ]
                }
            )
        )        

    fig.add_hline(y = 0, line_color = "#FF0000")
    fig.show()


def continuous(dfs: List[pl.DataFrame]):

    fig         = go.Figure()
    Y           = []
    A           = []
    T           = []
    i_          = 0

    for _, df in dfs.items():

        ts          = df["ts"]
        x           = np.array(df[x_sym])
        y           = np.array(df[y_sym])
        spread      = y * float(y_mult) - x * float(x_mult)
        mu          = np.cumsum(spread) / np.array([ i for i in range(1, len(spread) + 1) ])
        spread      = resample(spread, INTERVAL)
        mu          = resample(mu, INTERVAL)
        text        = resample(ts, INTERVAL)
        i_          = i_ + len(spread)
        
        fig.add_vline(
            x               = i_, 
            annotation_text = ts[0].split("T")[0], 
            line            = { "color": "#FF00FF" }
        )

        Y.extend(spread)
        A.extend(mu)
        T.extend(text)

    X       = [ i for i in range(len(Y)) ]
    traces  = [
                ( Y, "spread" ),
                ( A, "mean" )
            ]

    for trace in traces:

        fig.add_trace(
            go.Scattergl(
                {
                    "x":    X,
                    "y":    trace[0],
                    "name": trace[1],
                    "text": T
                }
            )
        )

    fig.show()


if __name__ == "__main__":

    t0              = time()
    folder          = argv[1]
    limit           = -int(argv[2]) if argv[2] != "-" else 0
    x_sym, x_mult   = argv[3].split(":")
    y_sym, y_mult   = argv[4].split(":")
    i_ts, j_ts      = argv[5].split("-")
    mode            = int(argv[6])
    dfs             = get_dfs(folder, limit, i_ts, j_ts, True)

    modes = {
        0: daily_demeaned,
        1: continuous
    }

    modes[mode](dfs)

    print(f"{time() - t0:0.1f}s")