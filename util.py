from    datetime    import  datetime
import  numpy       as      np
from    os          import  listdir
import  polars      as      pl
from    typing      import  List


def get_dfs(
    folder:         str,
    limit:          int,
    i_ts:           str,
    j_ts:           str,
    skip_weekend:   bool = True
) -> List[pl.DataFrame]:

    dates   = sorted(
                datetime.strptime(date[:-4], "%Y-%m-%d")
                for date in 
                listdir(f"./csvs/{folder}")
            )
    
    if skip_weekend:

        dates = [ date for date in dates if date.weekday() < 5 ]

    fns     = [ 
                f"./csvs/{folder}/{date.strftime('%Y-%m-%d')}.csv" 
                for date in dates 
            ][limit:]

    dfs     = { 
                fn[-14:-4]: pl.read_csv(fn).filter(
                                (pl.col("ts") >= f"{fn[-14:-4]}T{i_ts}") &
                                (pl.col("ts") <= f"{fn[-14:-4]}T{j_ts}")
                            )
                for fn in fns 
            }

    return dfs


def resample(
    a:          np.array,
    interval:   int
) -> np.array:
    
    a = [ a[i] for i in range(0, len(a), interval) ]

    return a