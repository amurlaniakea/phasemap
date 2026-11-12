.PHONY: test data verify serve

test:
	python -m pytest -q

data:
	python scripts/build_data.py
	python scripts/build_data_fase7.py

verify:
	python scripts/verify_release.py

serve:
	python -m http.server 8000
