import  numpy                   as      np
import  plotly.graph_objects    as      go
from    sklearn.linear_model    import  LinearRegression
from    sys                     import  argv
from    time                    import  time
from    typing                  import  List
from    util                    import  parse_args, reformat


# python x.py rty_emd - RTY:1 EMD:1 06-14 0


def betas(data: List[dict]):

    model = LinearRegression()
    betas = []

    for date, arrs in data.items():

        X   = np.log(arrs["x_mid"]) - np.log(arrs["x_mid"][0])
        Y   = np.log(arrs["y_mid"]) - np.log(arrs["y_mid"][0])
        
        X_  = X.reshape(-1, 1)

        model.fit(X_, Y)
        
        b   = model.coef_[0]
        a   = model.intercept_
        res = Y - model.predict(X_)

        betas.append(b)

        pass

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            {
                "x":    list(data.keys()),
                "y":    betas,
                "name": "test",
                "mode": "markers"
            }
        )
    )

    fig.show()


def static(data: List[dict]):

    alpha       = 0
    beta        = 0.70
    i_          = 0
    fig         = go.Figure()

    for date, arrs in data.items():

        X   = np.log(arrs["x_mid"]) - np.log(arrs["x_mid"][0])
        Y   = np.log(arrs["y_mid"]) - np.log(arrs["y_mid"][0])
        res = Y - (X * beta + alpha)

        fig.add_trace(
            go.Scattergl(
                {
                    "x":    [ i_ + i for i in range(len(res)) ],
                    "y":    res,
                    "name": date
                }
            )
        )

        i_ += len(res)

    fig.add_hline(y = 0, line_color = "#FF00FF")
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
        1: static
    }   
    
    modes[mode](data)

    print(f"{time() - t0:0.1f}s")