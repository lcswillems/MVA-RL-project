# Comparing EWF, Exp3, Exp3.P, CFR on mRPS

```
python main.py --game mRPS --algo EWF --eta .005 --iters 10000
```

```
python main.py --game mRPS --algo Exp3 --eta .005 --iters 10000
```

```
python main.py --game mRPS --algo Exp3P --eta .005 --gamma .01 --beta .05 --iters 10000
```

```
python main.py --game mRPS --algo CFR --iters 10000
```

# Comparing CFR, CFR+ on mRPS

```
python main.py --game mRPS --algo CFR --iters 500
```

```
python main.py --game mRPS --algo CFRp --iters 500
```