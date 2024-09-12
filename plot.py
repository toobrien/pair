from    bisect                  import  bisect_left
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    polars                  import  read_csv
from    math                    import  e, log
from    numpy                   import  arange, array, mean
from    sklearn.linear_model    import  LinearRegression
from    sys                     import  argv


# python plot.py ES:5 NQ:2 2024-07-03 06-15 live


def regress(
    x_sym:      str,
    x_mult:     float,
    y_sym:      str,
    y_mult:     float,
    date:       str,
    start_t:    str,
    end_t:      str,
    folder:     str
):
    
    df      = read_csv(f"./csvs/{folder}/{date}.csv")
    ts      = list(df["ts"])
    i       = bisect_left(ts, f"{date}T{start_t}")
    j       = bisect_left(ts, f"{date}T{end_t}")
    ts      = ts[i:j]
    x       = list(df[x_sym])[i:j]
    y       = list(df[y_sym])[i:j]
    spread  = list(df[y_sym][i:j] * y_mult - df[x_sym][i:j] * x_mult)
    model   = LinearRegression()

    x0  = x[0]
    y0  = y[0]
    x_  = array([ log(i / x0) for i in x ])
    y_  = array([ log(i / y0) for i in y ])

    model.fit(x_.reshape(-1, 1), y_)

    X           = arange(min(x_), max(x_), step = 0.00001)
    Y           = model.predict(X.reshape(-1, 1))
    b           = model.coef_[0]
    a           = model.intercept_
    residuals   = y_ - model.predict(x_.reshape(-1, 1))
    res_x       = [ i for i in range(len(residuals)) ]
    m_spread    = mean(spread)
    r_spread    = max(spread) - min(spread)
    o_spread    = [ x - m_spread for x in spread ]

    text        = [
                    f"{ts[i]}<br>x:{x[i]:>10.2f}<br>y:{y[i]:>10.2f}<br>s:{spread[i]:>10.2f}<br>r:{residuals[i]:>10.4f}<br>o:{o_spread[i]:>10.2f}"
                    for i in range(len(ts))
                ]
    latest      = text[-1].split(":")[0][-2:] # most recent hour
    color       = [ "#FF0000" if latest in text[i].split(":")[0][-2:] else "#0000FF" for i in range(len(text)) ]
    fig         = make_subplots(
                    rows                = 2,
                    cols                = 2,
                    column_widths       = [ 0.7, 0.3 ],
                    row_heights         = [ 0.6, 0.4 ],
                    vertical_spacing    = 0.025,
                    horizontal_spacing  = 0.025,
                    specs               = [ 
                                            [ {}, {} ], 
                                            [ 
                                                { 
                                                    "colspan":      2, 
                                                    "secondary_y":  True
                                                },
                                                None
                                            ] 
                                        ]
                )
    
    fig.add_trace(
        go.Scattergl(
            {
                "x":            x_,
                "y":            y_,
                "text":         text,
                "mode":         "markers",
                "marker":       { "color": color },
                "name":         "mid"
            }
        ),
        row = 1,
        col = 1
    )

    fig.add_trace(
        go.Scattergl(
            {
                "x":            X,
                "y":            Y,
                "text":         [   
                                    f"{x0* e**X[i]:0.2f}<br>{y0 * e**Y[i]:0.2f}" 
                                    for i in range(len(X)) 
                                ],
                "name":         f"model",
                "mode":         "lines",
                "line":         { "width": 2 },
                "line_color":   "#FF00FF",
                "opacity":      0.75
            }
        ),
        row = 1,
        col = 1
    )

    fig.add_trace(
        go.Scattergl(
            {
                "x":        [ x_[-1] ],
                "y":        [ y_[-1] ],
                "name":     f"last",
                "text":     [ f"{x[-1]:0.2f}<br>{y[-1]:0.2f}" ],
                "marker":   { "color": "#00FF00" }
            }
        ),
        row = 1,
        col = 1
    )

    fig.add_trace(
        go.Histogram(
            {
                "x":        residuals,
                "opacity":  0.5,
                "name":     f"res hist",
            }
        ),
        row = 1,
        col = 2
    )

    fig.add_trace(
        go.Scattergl(
            {
                "x":            res_x,
                "y":            residuals,
                "text":         text,
                "name":         f"res plot"
            }
        ),
        secondary_y = False,
        row         = 2,
        col         = 1
    )

    fig.add_trace(
        go.Scattergl(
            {
                "x":            res_x,
                "y":            o_spread,
                "text":         text,
                "name":         "spread"
                
            }
        ),
        secondary_y = True,
        row         = 2,
        col         = 1
    )

    fig.add_hline(y = 0, row = 2, col = 1, line_color = "#FF0000")

    title = f"{x_sym}, {y_sym}\t{date}T{start_t} - {end_t}\tb: {b:0.4f}\ta: {a:0.4f}\ts_mu: {m_spread:0.2f}\ts_rng: {r_spread:0.2f}"

    fig.update_layout(title_text = title)
    fig.show()


if __name__ == "__main__":

    x_sym, x_mult   = argv[1].split(":")
    y_sym, y_mult   = argv[2].split(":")
    x_mult          = float(x_mult)
    y_mult          = float(y_mult)
    date            = argv[3]
    rng             = argv[4].split("-")
    folder          = argv[5]

    regress(x_sym, x_mult, y_sym, y_mult, date, rng[0], rng[1], folder)