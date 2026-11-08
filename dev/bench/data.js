window.BENCHMARK_DATA = {
  "lastUpdate": 1794158049698,
  "repoUrl": "https://github.com/nardi/cyhighs",
  "entries": {
    "benchmarks-windows-latest": [
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
        "date": 1784279506431,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[lp-100]",
            "value": 440.0149605085695,
            "unit": "iter/sec",
            "range": "stddev: 0.000056914385030679395",
            "extra": "mean: 2.2726500000004535 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[lp-1000]",
            "value": 22.92053450686696,
            "unit": "iter/sec",
            "range": "stddev: 0.00026678156275046093",
            "extra": "mean: 43.6289999999957 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[lp-10000]",
            "value": 0.08844160298947906,
            "unit": "iter/sec",
            "range": "stddev: 0.044379516016367734",
            "extra": "mean: 11.306895919999993 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[mip-100]",
            "value": 103.18362764744354,
            "unit": "iter/sec",
            "range": "stddev: 0.0005370282533358585",
            "extra": "mean: 9.691459999999097 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[mip-1000]",
            "value": 0.06569409217246652,
            "unit": "iter/sec",
            "range": "stddev: 0.09436908793820203",
            "extra": "mean: 15.222068940000003 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[lp-100]",
            "value": 507.48283439579353,
            "unit": "iter/sec",
            "range": "stddev: 0.00005789955764657902",
            "extra": "mean: 1.9705099999896445 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[lp-1000]",
            "value": 23.734004467687328,
            "unit": "iter/sec",
            "range": "stddev: 0.001593821540413663",
            "extra": "mean: 42.13364000000297 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[lp-10000]",
            "value": 0.08755982369535305,
            "unit": "iter/sec",
            "range": "stddev: 0.2727909762839996",
            "extra": "mean: 11.42076305999999 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[mip-100]",
            "value": 110.79080259088542,
            "unit": "iter/sec",
            "range": "stddev: 0.00027728557200366205",
            "extra": "mean: 9.026019999987511 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[mip-1000]",
            "value": 0.06387446702961083,
            "unit": "iter/sec",
            "range": "stddev: 0.33156714771016677",
            "extra": "mean: 15.655707929999972 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[lp-100]",
            "value": 470.871866353365,
            "unit": "iter/sec",
            "range": "stddev: 0.00009457495323865227",
            "extra": "mean: 2.1237199999745826 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[lp-1000]",
            "value": 23.13333103541698,
            "unit": "iter/sec",
            "range": "stddev: 0.0019897691072093084",
            "extra": "mean: 43.22767000001022 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[lp-10000]",
            "value": 0.08825122094527227,
            "unit": "iter/sec",
            "range": "stddev: 0.06207549805310725",
            "extra": "mean: 11.331287989999998 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[mip-100]",
            "value": 111.90200964837541,
            "unit": "iter/sec",
            "range": "stddev: 0.00014364383772727472",
            "extra": "mean: 8.936389999985295 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[mip-1000]",
            "value": 0.0652172886438289,
            "unit": "iter/sec",
            "range": "stddev: 0.15253267264999798",
            "extra": "mean: 15.33335747 sec\nrounds: 10"
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
        "date": 1794158047706,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[lp-100]",
            "value": 547.6811181454005,
            "unit": "iter/sec",
            "range": "stddev: 0.00003387846907700945",
            "extra": "mean: 1.8258800000012343 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[lp-1000]",
            "value": 27.731097097661962,
            "unit": "iter/sec",
            "range": "stddev: 0.001264020109727669",
            "extra": "mean: 36.06060000000184 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[lp-10000]",
            "value": 0.11076733901304249,
            "unit": "iter/sec",
            "range": "stddev: 0.03412625655406791",
            "extra": "mean: 9.02793195999999 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[mip-100]",
            "value": 127.87331335107477,
            "unit": "iter/sec",
            "range": "stddev: 0.00008245851751800209",
            "extra": "mean: 7.820239999995238 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_array_solve[mip-1000]",
            "value": 0.0814432443307307,
            "unit": "iter/sec",
            "range": "stddev: 0.11851998758225289",
            "extra": "mean: 12.278489249999996 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[lp-100]",
            "value": 624.6018163449849,
            "unit": "iter/sec",
            "range": "stddev: 0.00015293086892029584",
            "extra": "mean: 1.601019999992559 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[lp-1000]",
            "value": 29.876261487796263,
            "unit": "iter/sec",
            "range": "stddev: 0.00020076126478666025",
            "extra": "mean: 33.4713899999997 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[lp-10000]",
            "value": 0.11005961645469532,
            "unit": "iter/sec",
            "range": "stddev: 0.032950988368244866",
            "extra": "mean: 9.085984780000008 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[mip-100]",
            "value": 129.4997940954239,
            "unit": "iter/sec",
            "range": "stddev: 0.00011385128508049208",
            "extra": "mean: 7.722019999994245 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_sparse_solve[mip-1000]",
            "value": 0.08160619133769555,
            "unit": "iter/sec",
            "range": "stddev: 0.25308150975516247",
            "extra": "mean: 12.253972199999975 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[lp-100]",
            "value": 602.5112669573518,
            "unit": "iter/sec",
            "range": "stddev: 0.0000359500827102062",
            "extra": "mean: 1.6597200000092016 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[lp-1000]",
            "value": 28.818726177710094,
            "unit": "iter/sec",
            "range": "stddev: 0.00024949313597366054",
            "extra": "mean: 34.6996600000125 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[lp-10000]",
            "value": 0.10718453190522893,
            "unit": "iter/sec",
            "range": "stddev: 0.24285151722510512",
            "extra": "mean: 9.32970441 sec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[mip-100]",
            "value": 129.8379233204611,
            "unit": "iter/sec",
            "range": "stddev: 0.0001255150230208836",
            "extra": "mean: 7.701909999991585 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_linprog_solve[mip-1000]",
            "value": 0.08109365235057184,
            "unit": "iter/sec",
            "range": "stddev: 0.08475624164402559",
            "extra": "mean: 12.331421399999977 sec\nrounds: 10"
          }
        ]
      }
    ]
  }
}