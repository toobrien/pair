from    bisect                  import  bisect_left
import  numpy                   as      np
import  polars                  as      pl
import  plotly.graph_objects    as      go
from    sys                     import  argv


# python 2024-09-30 06:30 live


if __name__ == "__main__":

    date    = argv[1]
    start   = f"{date}T{argv[2]}"
    mode    = argv[3]
    df      = pl.read_csv(f"./csvs/{mode}/{date}.csv")
    ts      = list(df["ts"])
    i       = bisect_left(ts, start)
    ts      = ts[i:]
    fig     = go.Figure()

    for col in df.columns[1:]:

        if mode != "live" and "bid" in col or "ask" in col:

            continue

        y = np.log(np.array(df[col][i:]))
        y = y - y[0]

        fig.add_trace(
            go.Scattergl(
                {
                    "x":    ts,
                    "y":    y,
                    "name": col
                }
            )
        )

    fig.show()

