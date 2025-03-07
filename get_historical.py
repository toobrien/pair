from    databento   import  Historical
from    datetime    import  datetime, timedelta
import  numpy       as      np
import  polars      as      pl
from    sys         import  argv
from    time        import  time


CLIENT      = Historical()
DATE_FMT    = "%Y-%m-%d"
FMT         = "%Y-%m-%dT%H:%M:%S.%f+0000"

pl.Config.set_tbl_cols(-1)
pl.Config.set_tbl_rows(-1)


# python get_historical.py eq_ind 2024-09-18 - ESH5 NQH5 RTYH5 EMDH5 YMH5


def get_df(
    symbol: str, 
    start:  str, 
    end:    str
):
    
    args = {
            "dataset":  "GLBX.MDP3",
            "schema":   "bbo-1s",
            "stype_in": "raw_symbol",
            "symbols":  [ symbol ],
            "start":    start,
            "end":      end 
    }

    cost = CLIENT.metadata.get_cost(**args)
    size = CLIENT.metadata.get_billable_size(**args)

    try:

        df  = pl.from_pandas(
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
            ).drop_nulls() # ts_event can be null, for some reason
    
    except Exception as e:

        print(e)

        df = pl.DataFrame(), 0, 0

    return df, cost, size



if __name__ == "__main__":

    t0  = time()

    folder      = argv[1]
    start_date  = datetime.strptime(argv[2], DATE_FMT)
    end_date    = datetime.strptime(argv[3], DATE_FMT) if argv[3] != "-" else datetime.today()
    date_range  = [ 
                    date.strftime(DATE_FMT) 
                    for date in 
                    pl.date_range(start_date, end_date, interval = "1d", eager = True) 
                ]
    symbols     = argv[4:]

    for i in range(len(date_range) - 1):

        t_i         = time()
        start_date  = date_range[i]
        end_date    = date_range[i + 1]
        start_ts    = "0000"
        end_ts      = "0000"
        data        = {}
        total_cost  = 0
        skip_date   = False

        if (datetime.strptime(start_date, DATE_FMT).weekday() in ( 5, 6 )):

            # skip saturday and sunday

            print(f"\n{start_date:<15}{'weekend, skip':<15}")

            continue

        print(f"\n{start_date:<15}")

        for symbol in symbols:

            in_df, cost, size = get_df(symbol, start_date, end_date)

            print(f"{symbol:<15}{cost:<15.4f}{size:<15} ({size / 1073741824:0.2f} GB)")

            total_cost += cost

            if len(in_df) <= 1 or skip_date:

                skip_date = True

                continue

            sym         = symbol[:-2]
            ts          = in_df["ts"]
            bid         = in_df["bid_px_00"]
            ask         = in_df["ask_px_00"]
            mid         = (bid + ask) / 2
            last        = in_df["price"]
            qty         = in_df["size"]
            side        = in_df["side"]

            # start ts is the latest initial timestamp, as i do not know previous state
            # end ts is the latest timestamp of all symbols, as the same period is downloaded for each

            start_ts    = start_ts if start_ts > ts[0] else ts[0]
            end_ts      = end_ts if end_ts > ts[-1] else ts[-1]

            data[sym] = {
                        "ts":   ts,
                        "bid":  bid,
                        "ask":  ask,
                        "mid":  mid,
                        "last": last,
                        "qty":  qty,
                        "side": side
                    }
            
        if skip_date:

            continue

        start_ts    = (datetime.fromisoformat(start_ts).replace(microsecond = 0) + timedelta(seconds = 1))
        end_ts      = (datetime.fromisoformat(end_ts).replace(microsecond = 0) + timedelta(seconds = 1))
        cur_ts      = start_ts
        ts_rng      = []

        while cur_ts <= end_ts:

            ts_rng.append(cur_ts.strftime("%Y-%m-%dT%H:%M:%S"))

            cur_ts += timedelta(seconds = 1)

        out_df = pl.DataFrame(
                {
                    "ts": ts_rng
                }
            )

        for sym, vecs in data.items():

            ts      = vecs["ts"]
            N       = len(ts)
            idx     = np.searchsorted(ts, ts_rng)
            bid     = vecs["bid"]
            ask     = vecs["ask"]
            mid     = vecs["mid"]
            last    = vecs["last"]
            qty     = vecs["qty"]
            side    = vecs["side"]
        
            ts      = [ ts[int(i - 1)] if i < N else ts[-1] for i in idx ]
            bid     = [ bid[int(i - 1)] if i < N else bid[-1] for i in idx ]
            ask     = [ ask[int(i - 1)] if i < N else ask[-1] for i in idx ]
            mid     = [ mid[int(i - 1)] if i < N else mid[-1] for i in idx ]
            last    = [ last[int(i - 1)] if i < N else last[-1] for i in idx ]
            qty     = [ qty[int(i - 1)] if i < N else qty[-1] for i in idx ]
            side    = [ side[int(i - 1)] if i < N else side[-1] for i in idx ]

            out_df = out_df.with_columns(
                    [
                        pl.Series(f"{sym}_bid", bid),
                        pl.Series(f"{sym}_ask", ask),
                        pl.Series(sym, mid),
                        pl.Series(f"{sym}_last", last),
                        pl.Series(f"{sym}_qty",  qty),
                        pl.Series(f"{sym}_side", side)
                    ]
                )
        
        out_df.write_csv(f"./csvs/{folder}/{start_date}.csv")

        print(f"{'total':<15}{total_cost:<15.2f}{f'{time() - t_i:0.1f}s':<15}")

    print(f"{time() - t0:0.1f}s\n")