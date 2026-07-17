window.BENCHMARK_DATA = {
  "lastUpdate": 1784279186838,
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
      }
    ]
  }
}