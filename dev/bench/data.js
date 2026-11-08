window.BENCHMARK_DATA = {
  "lastUpdate": 1794157802849,
  "repoUrl": "https://github.com/nardi/cyhighs",
  "entries": {
    "benchmarks-macos-latest": [
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
        "date": 1784279143917,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[lp-100]",
            "value": 1321.1563235840813,
            "unit": "iter/sec",
            "range": "stddev: 0.00007036664582816934",
            "extra": "mean: 756.9126999953824 usec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[lp-1000]",
            "value": 41.32705316964579,
            "unit": "iter/sec",
            "range": "stddev: 0.0010590375713438864",
            "extra": "mean: 24.197224899995717 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[lp-10000]",
            "value": 0.1251437047343185,
            "unit": "iter/sec",
            "range": "stddev: 1.5340556988952827",
            "extra": "mean: 7.990813458200006 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[mip-100]",
            "value": 168.92866655968928,
            "unit": "iter/sec",
            "range": "stddev: 0.0013315832741551145",
            "extra": "mean: 5.919658399994887 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[mip-1000]",
            "value": 0.10026955485086086,
            "unit": "iter/sec",
            "range": "stddev: 1.3656391960338892",
            "extra": "mean: 9.973116979399999 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[lp-100]",
            "value": 449.1934372466371,
            "unit": "iter/sec",
            "range": "stddev: 0.0008613971685550654",
            "extra": "mean: 2.2262124000064887 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[lp-1000]",
            "value": 25.536736946750302,
            "unit": "iter/sec",
            "range": "stddev: 0.010599424850570183",
            "extra": "mean: 39.159270900006504 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[lp-10000]",
            "value": 0.1449353419074669,
            "unit": "iter/sec",
            "range": "stddev: 0.1522014900740124",
            "extra": "mean: 6.899628391800007 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[mip-100]",
            "value": 179.34901222742988,
            "unit": "iter/sec",
            "range": "stddev: 0.0009568028078864596",
            "extra": "mean: 5.5757206999942355 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[mip-1000]",
            "value": 0.10137251761521285,
            "unit": "iter/sec",
            "range": "stddev: 0.3008244152194773",
            "extra": "mean: 9.864606537600002 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[lp-100]",
            "value": 617.1346573555685,
            "unit": "iter/sec",
            "range": "stddev: 0.00014554380954616688",
            "extra": "mean: 1.620391900019058 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[lp-1000]",
            "value": 39.63002738003352,
            "unit": "iter/sec",
            "range": "stddev: 0.0009300394151651562",
            "extra": "mean: 25.233391600022514 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[lp-10000]",
            "value": 0.13513645880040173,
            "unit": "iter/sec",
            "range": "stddev: 1.219593553611463",
            "extra": "mean: 7.399927516799982 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[mip-100]",
            "value": 188.05240629409806,
            "unit": "iter/sec",
            "range": "stddev: 0.0006986071112258156",
            "extra": "mean: 5.317666600001303 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[mip-1000]",
            "value": 0.10014640164709233,
            "unit": "iter/sec",
            "range": "stddev: 0.46028147500414185",
            "extra": "mean: 9.985381237399997 sec\nrounds: 10"
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
        "date": 1794157801733,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[lp-100]",
            "value": 1260.4181437114216,
            "unit": "iter/sec",
            "range": "stddev: 0.00005274494371354768",
            "extra": "mean: 793.3875000048829 usec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[lp-1000]",
            "value": 39.54753037734775,
            "unit": "iter/sec",
            "range": "stddev: 0.0012081180300200338",
            "extra": "mean: 25.2860290000001 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[lp-10000]",
            "value": 0.18379961660187394,
            "unit": "iter/sec",
            "range": "stddev: 0.2844911295502391",
            "extra": "mean: 5.440707758199994 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[mip-100]",
            "value": 270.49050802766465,
            "unit": "iter/sec",
            "range": "stddev: 0.0002340390760714547",
            "extra": "mean: 3.696987400007856 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[mip-1000]",
            "value": 0.1304003421066017,
            "unit": "iter/sec",
            "range": "stddev: 0.05370473278749671",
            "extra": "mean: 7.66869153749999 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[lp-100]",
            "value": 1190.0159093351908,
            "unit": "iter/sec",
            "range": "stddev: 0.00004847469846273066",
            "extra": "mean: 840.3248999911739 usec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[lp-1000]",
            "value": 49.29731775815589,
            "unit": "iter/sec",
            "range": "stddev: 0.000059642925839988967",
            "extra": "mean: 20.285079299969766 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[lp-10000]",
            "value": 0.18242966657040374,
            "unit": "iter/sec",
            "range": "stddev: 0.19158634801236435",
            "extra": "mean: 5.481564587599996 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[mip-100]",
            "value": 274.19671535955274,
            "unit": "iter/sec",
            "range": "stddev: 0.00009280999100653885",
            "extra": "mean: 3.647016699994765 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[mip-1000]",
            "value": 0.12206842014295957,
            "unit": "iter/sec",
            "range": "stddev: 0.4741762615315144",
            "extra": "mean: 8.19212699589998 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[lp-100]",
            "value": 982.4711428436584,
            "unit": "iter/sec",
            "range": "stddev: 0.00006144062283120524",
            "extra": "mean: 1.0178416000144352 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[lp-1000]",
            "value": 43.356141134863826,
            "unit": "iter/sec",
            "range": "stddev: 0.000048429830327365986",
            "extra": "mean: 23.064783300003455 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[lp-10000]",
            "value": 0.1662896359772211,
            "unit": "iter/sec",
            "range": "stddev: 0.4559230142890315",
            "extra": "mean: 6.01360387929999 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[mip-100]",
            "value": 267.61818132792496,
            "unit": "iter/sec",
            "range": "stddev: 0.00010021233593168744",
            "extra": "mean: 3.736666899976626 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[mip-1000]",
            "value": 0.12238616838765942,
            "unit": "iter/sec",
            "range": "stddev: 0.6246713586158403",
            "extra": "mean: 8.170857975 sec\nrounds: 10"
          }
        ]
      }
    ]
  }
}