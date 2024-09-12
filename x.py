import  numpy                   as      np
import  plotly.graph_objects    as      go
from    sklearn.linear_model    import  LinearRegression
from    sys                     import  argv
from    time                    import  time
from    typing                  import  List
from    util                    import  parse_args, reformat


# python x.py rty_emd - RTY:1 EMD:1 06-14 0


def run(data: List[dict]):

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


if __name__ == "__main__":

    t0      = time()
    args    = parse_args(argv)
    x_args  = ( args['x_sym'], args['x_mult'] )
    y_args  = ( args['y_sym'], args['y_mult'] )
    data    = reformat(x_args, y_args, args['dfs'])
    
    run(data)

    print(f"{time() - t0:0.1f}s")