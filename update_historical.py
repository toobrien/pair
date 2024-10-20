from    bisect      import  bisect_left
from    databento   import  Historical
from    datetime    import  datetime, timedelta
import  numpy       as      np
from    os          import  listdir
import  polars      as      pl
from    sys         import  argv
from    time        import  time


CLIENT      = Historical()
DATE_FMT    = "%Y-%m-%d"
FMT         = "%Y-%m-%dT%H:%M:%S.%f+0000"


# python update_historical.py eq_ind 2024-06-18 2024-10-17 YMZ4


if __name__ == "__main__":

    t0          = time()
    folder      = f"./csvs/{argv[1]}"
    start_date  = argv[2]
    end_date    = argv[3]
    symbols     = argv[4:]
    fns         = sorted(listdir(folder))
    fns         = fns[bisect_left(fns, start_date) : bisect_left(fns, end_date) + 1]
    total_cost  = 0

    for fn in fns:

        start_date  = fn.split(".")[0]
        end_date    = (datetime.strptime(start_date, DATE_FMT) + timedelta(days = 1)).strftime(DATE_FMT)
        df          = pl.read_csv(f"{folder}/{fn}")
        ts          = np.array(df["ts"])

        for symbol in symbols:

            root = symbol[:-2]
            args = {
                "dataset":  "GLBX.MDP3",
                "schema":   "mbp-1",
                "stype_in": "raw_symbol",
                "symbols":  [ symbol ],
                "start":    start_date,
                "end":      end_date 
            }
            
            cost = CLIENT.metadata.get_cost(**args)
            size = CLIENT.metadata.get_billable_size(**args)

            print(f"{symbol + ' cost':<15}{cost:0.4f}")
            print(f"{symbol + ' size':<15}{size} ({size / 1073741824:0.2f} GB)")

            total_cost += cost

            try:

                df_ = pl.from_pandas(
                        CLIENT.timeseries.get_range(**args).to_df(),
                        include_index = False
                    ).with_columns(
                        pl.col(
                            "ts_event"
                        ).dt.convert_time_zone(
                            "America/Los_Angeles"
                        ).dt.strftime(
                            FMT
                        ).alias(
                            "ts"
                        )
                    )
            
            except Exception as e:

                print(e)

                df_ = pl.DataFrame()
            
            pass

            if df_.is_empty():

                continue

            ts_ = [ 
                    (
                        datetime.fromisoformat(t).replace(microsecond = 0)
                    ).strftime("%Y-%m-%dT%H:%M:%S") 
                    for t in df_["ts"]
                ]
            N   = len(ts_)
            idx = np.searchsorted(ts_, ts)
            bid = df_["bid_px_00"]
            ask = df_["ask_px_00"]
            mid = ((bid + ask) / 2)

            bid = [ bid[int(i - 1)] if i < N else bid[-1] for i in idx ]
            ask = [ ask[int(i - 1)] if i < N else ask[-1] for i in idx ]
            mid = [ mid[int(i - 1)] if i < N else mid[-1] for i in idx ]

            df  = df.with_columns(
                    [
                        pl.Series(f"{root}_bid", bid),
                        pl.Series(f"{root}_ask", ask),
                        pl.Series(root, mid)
                    ]
                )

        df.write_csv(f"./csvs/tmp/{start_date}.csv")
        
        pass

    print(f"total_cost:    ${total_cost:0.2f}")
    print(f"elapsed:        {time() - t0:0.1f}s")

    pass