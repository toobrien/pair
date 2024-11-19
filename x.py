from    bisect                  import  bisect_left
import  numpy                   as      np
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sklearn.linear_model    import  LinearRegression
from    sys                     import  argv
from    time                    import  time
from    typing                  import  List
from    util                    import  parse_args, reformat, resample


# python x.py eq_ind - RTY:1 EMD:1 06-14 t_rule


def betas(data: List[dict]):

    model   = LinearRegression()
    betas   = []
    alphas  = []

    for _, arrs in data.items():

        X   = np.log(arrs["x_mid"]) - np.log(arrs["x_mid"][0])
        Y   = np.log(arrs["y_mid"]) - np.log(arrs["y_mid"][0])
        
        X_  = X.reshape(-1, 1)

        model.fit(X_, Y)
        
        b   = model.coef_[0]
        a   = model.intercept_
        res = Y - model.predict(X_)

        betas.append(b)
        alphas.append(a)

        pass

    print(f"a: {np.mean(alphas)}")
    print(f"b: {np.mean(betas)}")

    fig     = go.Figure()
    X       = list(data.keys())
    traces  = [
                ( betas,  "betas",  "#0000FF" ),
                ( alphas, "alphas", "#FF0000" )
            ] 

    for trace in traces:

        fig.add_trace(
            go.Scatter(
                {
                    "x":        X,
                    "y":        trace[0],
                    "name":     trace[1],
                    "mode":     "markers",
                    "marker":   { "color": trace[2] }
                }
            )
        )

    fig.show()


def static(data: List[dict]):

    alpha       = 0.0005
    beta        = 0.7350
    i_          = 0
    fig         = go.Figure()

    for date, arrs in data.items():

        X       = np.log(arrs["x_mid"]) - np.log(arrs["x_mid"][0])
        Y       = np.log(arrs["y_mid"]) - np.log(arrs["y_mid"][0])
        spread  = arrs["spread"]
        res     = Y - (X * beta + alpha)
        text    = [
                    f"{date}<br>{arrs['ts'][i]}<br>{spread[i]:0.2f}"
                    for i in range(len(arrs["ts"]))
                ]

        fig.add_trace(
            go.Scattergl(
                {
                    "x":    [ i_ + i for i in range(len(res)) ],
                    "y":    res,
                    "name": date,
                    "text": text
                }
            )
        )

        i_ += len(res)

    fig.add_hline(y = 0, line_color = "#FF00FF")
    fig.show()


def t_rule(data: List[dict]):

    mode            = "Z"
    in_ts           = "11:30"
    out_ts          = "13:00"
    T               = 0.001 if mode == "R" else 2.0 if mode == "Z" else None
    resample_out    = True
    resample_freq   = 60
    model           = LinearRegression()
    C               = []
    text            = []
    prev            = 0

    for date, arrs in data.items():

        ts          = arrs["ts"]
        i           = bisect_left(ts, in_ts)
        j           = bisect_left(ts, out_ts)
        spread      = arrs["spread"]
        X           = np.log(arrs["x_mid"]) - np.log(arrs["x_mid"][0])
        Y           = np.log(arrs["y_mid"]) - np.log(arrs["y_mid"][0])
        
        model.fit(X[:i].reshape(-1, 1), Y[:i])

        Y_          = model.predict(X[i:j].reshape(-1, 1))
        residuals   = Y[i:j] - Y_
        z_res       = (residuals - np.mean(residuals)) / residuals.std()
        feature     = residuals if mode == "R" else z_res

        for i_ in range(len(feature)):

            if abs(feature[i_]) > T:

                pos     = -(feature[i_] / abs(feature[i_]))                                             # 1 or -1
                zero_i  = np.where(feature[i_:] > 0) if feature[i_] < 0 else np.where(feature[i_:] < 0) # return to fv
                m       = i + i_
                n       = m + zero_i[0][0] if len(zero_i[0]) > 0 else j                                 # sooner of return to fv, session close
                C_      = spread[m:n] * pos
                C_      = C_ - C_[0] + prev
                prev    = C_[-1]

                C.extend(C_)
                text.extend([ f"{date}<br>{ts_}<br>{int(pos)}" for ts_ in ts[m:n] ])

                break
        
    fig = go.Figure()
    X   = [ i for i in range(len(C)) ]

    if resample_out:

        X       = resample(X, resample_freq)
        C       = resample(C, resample_freq)
        text    = resample(text, resample_freq)

    fig.add_trace(
        go.Scattergl(
            {
                "x":    X,
                "y":    C,
                "name": "eqc",
                "text": text
            }
        )
    )

    fig.show()


def last(data: List[dict]):

    fig     = make_subplots(rows = 2, cols = 2)
    dates   = sorted(list(data.keys()))
    thresh  = 2.0
    highs   = []
    lows    = []

    for i in range(1, len(dates)):

        prev    = data[dates[i - 1]]["spread"]
        cur     = data[dates[i]]["spread"]
        prev_c  = prev[-1]
        high    = max(cur) - prev_c
        low     = min(cur) - prev_c

        highs.append(high)
        lows.append(low)

    X       = [ i for i in range(len(dates)) ]
    traces  = [
                ( highs, "#0000FF", "highs", 1 ),
                ( lows, "#FF0000", "lows", 2 )
            ]
    
    for trace in traces:

        fig.add_trace(
            go.Scatter(
                {
                    "x":        X,
                    "y":        trace[0],
                    "mode":     "markers",
                    "marker":   { "color": trace[1] },
                    "name":     trace[2],
                    "text":     dates[1:]
                }
            ),
            row = trace[3],
            col = 1
        )

        fig.add_trace(
            go.Histogram(
                x       = trace[0], 
                name    = trace[2], 
                xbins   = {
                            "start":    min(trace[0]),
                            "end":      max(trace[0]),
                            "size":     2
                        }
            ),
            row = trace[3], 
            col = 2
        )

    fig.add_hline(y = thresh, line_color = "#FF00FF", row = 1, col = 1)
    fig.add_vline(x = thresh, line_color = "#FF00FF", row = 1, col = 2)
    fig.add_hline(y = -thresh, line_color = "#FF00FF", row = 2, col = 1)
    fig.add_vline(x = -thresh, line_color = "#FF00FF", row = 2, col = 2)

    highs    = sorted(highs)
    lows     = sorted(lows)

    print(f"{'':10}{'mean':>10}{'stdev':>10}{'pct > t':>10}")
    print(f"{'hi':<10}{np.mean(highs):>10.2f}{np.std(highs):>10.2f}{1 - bisect_left(highs, thresh) / len(highs):>10.2f}")
    print(f"{'lo':<10}{np.mean(lows):>10.2f}{np.std(lows):>10.2f}{bisect_left(lows, -thresh) / len(lows):>10.2f}")
    print()

    fig.show()


if __name__ == "__main__":

    t0      = time()
    args    = parse_args(argv)
    x_args  = ( args['x_sym'], args['x_mult'] )
    y_args  = ( args['y_sym'], args['y_mult'] )
    data    = reformat(x_args, y_args, args['dfs'])
    mode    = args["mode"]

    modes = {
        "betas":    betas,
        "static":   static,
        "t_rule":   t_rule,
        "last":     last
    }   
    
    modes[mode](data)

    print(f"{time() - t0:0.1f}s")