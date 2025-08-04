# corregir_numpy.py (versión segura)
import subprocess
import sys
import importlib.util

def instalar_paquete(package):
    print(f"📦 Instalando {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def desinstalar_paquete(package):
    print(f"🗑 Desinstalando {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", package])
    except subprocess.CalledProcessError:
        print(f"ℹ️ {package} no estaba instalado.")

def verificar_numpy():
    spec = importlib.util.find_spec("numpy")
    if spec is None:
        return None
    module = importlib.import_module("numpy")
    version = getattr(module, '__version__', 'desconocida')
    return version

def main():
    print("🔧 Corrigiendo numpy... (NO uses 'streamlit run'. Usa 'python corregir_numpy.py')")

    # 1. Detener si se ejecuta con Streamlit
    if "streamlit" in sys.modules:
        print("❌ No ejecutes este script con 'streamlit run'. Usa 'python corregir_numpy.py'")
        return

    # 2. Verificar numpy
    version = verificar_numpy()
    if version:
        print(f"🔢 numpy v{version}")
        if version.startswith("2."):
            print("⚠️ numpy 2.x detectado. Corrigiendo...")
            desinstalar_paquete("numpy")
            instalar_paquete("numpy==1.26.4")
        else:
            print("✅ numpy es compatible.")
    else:
        print("🔢 numpy no encontrado. Instalando...")
        instalar_paquete("numpy==1.26.4")

    print("✅ Corrección completada. Ahora ejecuta: streamlit run streamlit_app.py")

if __name__ == "__main__":
    main()
