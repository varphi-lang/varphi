ifeq ($(OS),Windows_NT)
EXE_NAME ?= vpi
VENV_ACTIVATE = Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process; venv\\Scripts\\activate
ANTLR_GRAMMAR_FILE = Varphi.g4
ANTLR_VERSION = 4.13.2
ANTLR_JAR_FILE = antlr-$(ANTLR_VERSION)-complete.jar
ANTLR_JAR_DOWNLOAD_LINK = https://www.antlr.org/download/$(ANTLR_JAR_FILE)
ANTLR_OUTPUT_DIR = varphi\parsing

$(ANTLR_JAR_FILE):
	powershell -Command "Invoke-WebRequest -Uri $(ANTLR_JAR_DOWNLOAD_LINK) -OutFile $(ANTLR_JAR_FILE)"

parsing: $(ANTLR_JAR_FILE)
	powershell -Command "java -jar $(ANTLR_JAR_FILE) -Dlanguage=Python3 -o $(ANTLR_OUTPUT_DIR) $(ANTLR_GRAMMAR_FILE)"

venv:
	python -m venv venv

install: venv parsing
	powershell -Command "$(VENV_ACTIVATE); pip install ."

test: install
	powershell -Command "$(VENV_ACTIVATE); pip install pytest pytest-cov; pytest --cov=varphi tests/"

lint: install
	powershell -Command "$(VENV_ACTIVATE); pip install pylint; pylint varphi/"

executable: install
	powershell -Command "$(VENV_ACTIVATE); pip install pyinstaller; pyinstaller --onefile --optimize 2 varphi_interpreter/vpi.py --distpath ./bin --noconfirm --hidden-import varphi --hidden-import argparse --name $(EXE_NAME)"

clean:
	powershell -Command "Remove-Item -Recurse -Force *.pyc, __pycache__, varphi\\parsing\\Varphi*.py, varphi\\parsing\\*.tokens, varphi\\parsing\\*.interp, vpi.spec, venv, bin, varphi.egg-info, build, .pytest_cache, antlr-4.13.2-complete.jar, .coverage -ErrorAction SilentlyContinue; exit 0"


else
EXE_NAME ?= vpi
VENV_ACTIVATE = . venv/bin/activate
ANTLR_GRAMMAR_FILE = Varphi.g4
ANTLR_VERSION = 4.13.2
ANTLR_JAR_FILE = antlr-$(ANTLR_VERSION)-complete.jar
ANTLR_JAR_DOWNLOAD_LINK = https://www.antlr.org/download/$(ANTLR_JAR_FILE)
ANTLR_OUTPUT_DIR = varphi/parsing

$(ANTLR_JAR_FILE):
	curl -L $(ANTLR_JAR_DOWNLOAD_LINK) -o $(ANTLR_JAR_FILE)

parsing: $(ANTLR_JAR_FILE)
	java -jar $(ANTLR_JAR_FILE) -Dlanguage=Python3 -o $(ANTLR_OUTPUT_DIR) $(ANTLR_GRAMMAR_FILE)

venv:
	python -m venv venv

install: venv parsing
	$(VENV_ACTIVATE) && pip install .

test: install
	$(VENV_ACTIVATE) && pip install pytest pytest-cov && pytest --cov=varphi tests/

lint: install
	$(VENV_ACTIVATE) && pip install pylint && pylint varphi/

executable: install
	$(VENV_ACTIVATE) && pip install pyinstaller && pyinstaller --onefile --optimize 2 varphi_interpreter/vpi.py --distpath ./bin --noconfirm --hidden-import varphi --hidden-import argparse --name $(EXE_NAME)

clean:
	find . -type f -name "*.pyc" -exec rm -f {} +; \
	find . -type d -name "__pycache__" -exec rm -rf {} +;
	rm -f varphi/parsing/Varphi*.py varphi/parsing/*.tokens varphi/parsing/*.interp vpi.spec || echo "Files not found, skipping..."
	rm -rf venv bin varphi.egg-info build .pytest_cache || echo "Directories not found, skipping..."
	rm -f antlr-4.13.2-complete.jar .coverage || echo "File not found, skipping..."
endif
