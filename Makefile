# Makefile Clonado Esteticamente
LINE = ===========================================================
# Definimos el comando estricto. Si no tienes python3.13 instalado, esto fallará a propósito.
PYTHON_BIN = python3.13

install:
	@echo ""
	@echo "$(LINE)"
	@echo "   INSTALACION AUTOMATICA DEL PROYECTO ML"
	@echo "$(LINE)"
	@echo ""
	
	@echo "[PASO 1] Buscando Python 3.13..."
	@echo "$(LINE)"
	@# Verifica si el binario existe. Si no, aborta con error.
	@which $(PYTHON_BIN) > /dev/null || (echo " [ERROR CRITICO] No se encontro $(PYTHON_BIN). Instala Python 3.13." && exit 1)
	@echo " [OK] Se encontro $(PYTHON_BIN)."
	@echo ""

	@echo "[PASO 2] Creando Entorno Virtual..."
	@echo "$(LINE)"
	@$(PYTHON_BIN) -m venv venv || (echo " [ERROR] Fallo al crear venv." && exit 1)
	@echo " [OK] Carpeta 'venv' creada exitosamente."
	@echo ""

	@echo "[PASO 3] Instalando librerias (esto puede tardar)..."
	@echo "$(LINE)"
	@. venv/bin/activate && pip install -r requirements.txt
	@echo ""

	@echo "[PASO 4] Instalando binarios de Playwright..."
	@echo "$(LINE)"
	@. venv/bin/activate && playwright install
	@echo ""

	@echo ""
	@echo "$(LINE)"
	@echo "$(LINE)"
	@echo "   INSTALACION COMPLETADA CON EXITO"
	@echo "$(LINE)"
	@echo "$(LINE)"
	@echo ""
	@echo " Para comenzar a trabajar, escribe:"
	@echo ""
	@echo "     source venv/bin/activate"
	@echo ""

clean:
	rm -rf venv
	rm -rf __pycache__
	rm -rf src/__pycache__