from    bisect                  import  bisect_left
import  numpy                   as      np
import  polars                  as      pl
import  plotly.graph_objects    as      go
from    sys                     import  argv


# python 06:30-14:00 live 2024-09-30


if __name__ == "__main__":

    date    = argv[3]
    bounds  = argv[1].split("-")
    start   = f"{date}T{bounds[0]}"
    end     = f"{date}T{bounds[1]}"
    mode    = argv[2]
    df      = pl.read_csv(f"./csvs/{mode}/{date}.csv")
    ts      = list(df["ts"])
    i       = bisect_left(ts, start)
    j       = bisect_left(ts, end)
    ts      = ts[i:j]
    fig     = go.Figure()

    for col in df.columns[1:]:

        if mode != "live" and "bid" in col or "ask" in col:

            continue

        y   = df[col][i:j]
        y_  = np.log(np.array(y)) - np.log(y[0])

        fig.add_trace(
            go.Scattergl(
                {
                    "x":    ts,
                    "y":    y_,
                    "name": col,
                    "text": y
                }
            )
        )

    fig.add_hline(y = 0, line_color = "#FF00FF")
    fig.show()

