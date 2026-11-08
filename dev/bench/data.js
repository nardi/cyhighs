window.BENCHMARK_DATA = {
  "lastUpdate": 1794158014690,
  "repoUrl": "https://github.com/nardi/cyhighs",
  "entries": {
    "benchmarks-ubuntu-latest": [
      {
        "commit": {
          "author": {
            "email": "mail@nardilam.nl",
            "name": "Nardi Lam",
            "username": "nardi"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "8a22b41c0523398626bde455b19990be9a31c915",
          "message": "Add performance benchmarks with CI regression tracking (#10)\n\n* Add performance benchmarks with CI regression tracking\n\nAdd a pytest-benchmark suite that measures solve time across all three public\ninterfaces (array, sparse, and linprog) on generated LPs and mixed integer\nprograms of increasing size. LPs run at 100, 1000 and 10000 variables and MIPs\nat 100 and 1000, each with twice as many constraints as variables.\n\nThe generators build feasible, bounded, seeded instances so timings stay\ncomparable across commits, and each benchmark asserts optimality so a broken\nsolve is caught. The suite lives outside the default test paths so a plain\npytest run and the wheel test steps are unaffected.\n\nWire regression tracking into the existing test job on Ubuntu, Windows and\nmacOS using github-action-benchmark. Each operating system tracks its own\nseries on its own data branch, comparing against stored history and commenting\non a regression past 120 percent. The alert is advisory and never fails the\nbuild, since hosted runners are too noisy for a hard threshold.",
          "timestamp": "2026-07-17T10:55:37+02:00",
          "tree_id": "3903b3729ac52a95d3bb63d6c2f734c171526801",
          "url": "https://github.com/nardi/cyhighs/commit/8a22b41c0523398626bde455b19990be9a31c915"
        },
        "date": 1784279186082,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[lp-100]",
            "value": 777.233101456788,
            "unit": "iter/sec",
            "range": "stddev: 0.00007331256211535615",
            "extra": "mean: 1.2866152999990277 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[lp-1000]",
            "value": 34.82034632086863,
            "unit": "iter/sec",
            "range": "stddev: 0.0011065957488331692",
            "extra": "mean: 28.718841299998132 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[lp-10000]",
            "value": 0.13090608970390633,
            "unit": "iter/sec",
            "range": "stddev: 0.0732322434031961",
            "extra": "mean: 7.6390640211 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[mip-100]",
            "value": 192.67692428504841,
            "unit": "iter/sec",
            "range": "stddev: 0.00031427658116649925",
            "extra": "mean: 5.190035100002888 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[mip-1000]",
            "value": 0.0876368448410911,
            "unit": "iter/sec",
            "range": "stddev: 0.1586581600130703",
            "extra": "mean: 11.410725726300004 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[lp-100]",
            "value": 696.0141981312497,
            "unit": "iter/sec",
            "range": "stddev: 0.000022327899883809834",
            "extra": "mean: 1.4367523000032634 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[lp-1000]",
            "value": 33.302138332298114,
            "unit": "iter/sec",
            "range": "stddev: 0.0021727177507363834",
            "extra": "mean: 30.028101800002105 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[lp-10000]",
            "value": 0.1315023074896695,
            "unit": "iter/sec",
            "range": "stddev: 0.08971279272085499",
            "extra": "mean: 7.604429299299994 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[mip-100]",
            "value": 183.30126233304014,
            "unit": "iter/sec",
            "range": "stddev: 0.0000602145582712725",
            "extra": "mean: 5.455499800012831 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[mip-1000]",
            "value": 0.08918030063429981,
            "unit": "iter/sec",
            "range": "stddev: 0.1397117698885482",
            "extra": "mean: 11.21323871849999 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[lp-100]",
            "value": 766.8958074624117,
            "unit": "iter/sec",
            "range": "stddev: 0.0000230580133124934",
            "extra": "mean: 1.3039581000043654 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[lp-1000]",
            "value": 32.69740873332307,
            "unit": "iter/sec",
            "range": "stddev: 0.002101361619337457",
            "extra": "mean: 30.58346329997903 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[lp-10000]",
            "value": 0.131812978927733,
            "unit": "iter/sec",
            "range": "stddev: 0.09057955846089433",
            "extra": "mean: 7.586506337499998 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[mip-100]",
            "value": 198.77732070009353,
            "unit": "iter/sec",
            "range": "stddev: 0.000047917507329365796",
            "extra": "mean: 5.030755000007048 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[mip-1000]",
            "value": 0.09122154417035709,
            "unit": "iter/sec",
            "range": "stddev: 0.17985829651655016",
            "extra": "mean: 10.962322651899978 sec\nrounds: 10"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "mail@nardilam.nl",
            "name": "Nardi Lam",
            "username": "nardi"
          },
          "committer": {
            "email": "mail@nardilam.nl",
            "name": "Nardi Lam",
            "username": "nardi"
          },
          "distinct": false,
          "id": "09976cbaa725646daba565935bae89d899c95d0f",
          "message": "chore: Update Zensical to 0.1.0 and switch to the Tufte theme\n\nThe `theme` submodule holds `zensical-tufte`, and `custom_dir` points at its directory, which extends the built-in theme. The theme loads its own fonts, so the built-in one loads none from Google Fonts, and the exclude plugin leaves the theme's packaging files out of the site. The switcher names cyhighs as the current one. The workflow checks out the submodule.",
          "timestamp": "2026-11-08T17:51:31+01:00",
          "tree_id": "81770ecf013cffd9c7a05f3cc1d0d10b48c21694",
          "url": "https://github.com/nardi/cyhighs/commit/09976cbaa725646daba565935bae89d899c95d0f"
        },
        "date": 1794158014136,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[lp-100]",
            "value": 701.2113285454567,
            "unit": "iter/sec",
            "range": "stddev: 0.0000991621056408675",
            "extra": "mean: 1.426103600000772 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[lp-1000]",
            "value": 29.253485881214004,
            "unit": "iter/sec",
            "range": "stddev: 0.0005730723576235739",
            "extra": "mean: 34.18396029999897 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[lp-10000]",
            "value": 0.11218728470708943,
            "unit": "iter/sec",
            "range": "stddev: 0.0321814244351162",
            "extra": "mean: 8.913666130800001 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[mip-100]",
            "value": 154.1368630839118,
            "unit": "iter/sec",
            "range": "stddev: 0.00010335627855159226",
            "extra": "mean: 6.487740700001154 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[mip-1000]",
            "value": 0.08115969730761552,
            "unit": "iter/sec",
            "range": "stddev: 0.168806405524242",
            "extra": "mean: 12.321386515400004 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[lp-100]",
            "value": 662.1306742744457,
            "unit": "iter/sec",
            "range": "stddev: 0.00003235735975316031",
            "extra": "mean: 1.5102758999887556 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[lp-1000]",
            "value": 29.732354783258295,
            "unit": "iter/sec",
            "range": "stddev: 0.00017715470728187007",
            "extra": "mean: 33.633393900004194 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[lp-10000]",
            "value": 0.11444115581535096,
            "unit": "iter/sec",
            "range": "stddev: 0.05947275753734265",
            "extra": "mean: 8.73811517260001 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[mip-100]",
            "value": 159.9215437700706,
            "unit": "iter/sec",
            "range": "stddev: 0.00005082376424971821",
            "extra": "mean: 6.253066199997193 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[mip-1000]",
            "value": 0.0826257618919635,
            "unit": "iter/sec",
            "range": "stddev: 0.024794987261128627",
            "extra": "mean: 12.102762832099994 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[lp-100]",
            "value": 624.6194115834547,
            "unit": "iter/sec",
            "range": "stddev: 0.00002348454767228362",
            "extra": "mean: 1.6009749000033935 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[lp-1000]",
            "value": 29.6916778463846,
            "unit": "iter/sec",
            "range": "stddev: 0.0001353345453129354",
            "extra": "mean: 33.67947090001735 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[lp-10000]",
            "value": 0.11373377435363874,
            "unit": "iter/sec",
            "range": "stddev: 0.055915827594654466",
            "extra": "mean: 8.792462974900001 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[mip-100]",
            "value": 153.10747857177975,
            "unit": "iter/sec",
            "range": "stddev: 0.000054065728699669336",
            "extra": "mean: 6.531359599989628 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[mip-1000]",
            "value": 0.0814557654863235,
            "unit": "iter/sec",
            "range": "stddev: 0.07341430597641724",
            "extra": "mean: 12.27660183449999 sec\nrounds: 10"
          }
        ]
      }
    ]
  }
}