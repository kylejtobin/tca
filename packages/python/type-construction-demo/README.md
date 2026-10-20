# type-construction-demo

The TCA demo program: the shop. A customer's order is priced by the promotions system and charged at the payment provider, and answered as paid, declined or unsettled; it is served over HTTP.

`src/type_construction/demo` is the program in the layout `tca-python-dev` names: `domain/checkout/{type,value,record,connections,order}.py`, `api/checkout.py`, `config.py`, and `main.py`, one call that serves the config. `nouns.json` is its noun list. `tests/type_construction_demo/test_checkout.py` crosses it over a bound socket as a customer would. The `tca-python-demo` skill's pages are copies of its files.

Run it: `PROMOTIONS__URL=... PAYMENTS__URL=... PAYMENTS__KEY=... python -m type_construction.demo.main`, with `HTTP_HOST` and `HTTP_PORT` as the bind.
