from    bisect                  import  bisect_left
import  numpy                   as      np
import  plotly.graph_objects    as      go
from    sklearn.linear_model    import  LinearRegression
from    sys                     import  argv
from    time                    import  time
from    typing                  import  List
from    util                    import  parse_args, reformat


# python x.py rty_emd - RTY:1 EMD:1 06-14 0


def betas(data: List[dict]):

    model   = LinearRegression()
    betas   = []
    alphas  = []

    for date, arrs in data.items():

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

    in_ts   = "11:30"
    out_ts  = "13:00"
    T       = 0.001
    model   = LinearRegression()
    C       = []
    text    = []
    prev    = 0

    for date, arrs in data.items():

        ts          = arrs["ts"]
        i           = bisect_left(ts, in_ts)
        j           = bisect_left(ts, out_ts)
        spread      = arrs["spread"][i:]
        X           = np.log(arrs["x_mid"]) - np.log(arrs["x_mid"][0])
        Y           = np.log(arrs["y_mid"]) - np.log(arrs["y_mid"][0])
        
        model.fit(X[:i].reshape(-1, 1), Y[:i])

        Y_          = model.predict(X[i:].reshape(-1, 1))
        residuals   = Y[i:] - Y_

        for i_ in range(len(residuals)):

            if abs(residuals[i_]) > T:

                pos     = -(residuals[i_] / abs(residuals[i_])) # 1 or -1
                C_      = spread[i_:j] * pos
                C_      = C_ - C_[0] + prev
                prev    = C_[-1]

                C.extend(C_)
                text.extend([ f"{date}T{ts_}" for ts_ in ts[i_:j] ])

                break
        
    fig = go.Figure()

    fig.add_trace(
        go.Scattergl(
            {
                "x":    [ i for i in range(len(C) - 1) ],
                "y":    C,
                "name": "eqc",
                "text": text
            }
        )
    )

    fig.show()


if __name__ == "__main__":

    t0      = time()
    args    = parse_args(argv)
    x_args  = ( args['x_sym'], args['x_mult'] )
    y_args  = ( args['y_sym'], args['y_mult'] )
    data    = reformat(x_args, y_args, args['dfs'])
    mode    = args["mode"]

    modes = {
        0: betas,
        1: static,
        2: t_rule
    }   
    
    modes[mode](data)

    print(f"{time() - t0:0.1f}s")