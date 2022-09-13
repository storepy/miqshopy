# MIQ SHOP BACKEND APP

```
python3 -m venv shopyenv
pip3 install -e {/path/to/miq/}
pip3 install -e {/path/to/miq/}\[dev\]
pip3 install -e .

```

```
coverage run -m pytest

<!-- if print statements -->
coverage run -m pytest shopy/sales/tests/test_customer_viewset.py::TestCustomerViewSet::test_list --capture=no

```
