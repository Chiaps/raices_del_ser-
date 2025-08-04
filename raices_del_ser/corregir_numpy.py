# corregir_numpy.py
# Script automático para corregir el error de numpy 2.x incompatible con Streamlit

import subprocess
import sys
import importlib.util
import os

def instalar_paquete(package):
    """Instala un paquete usando pip."""
    print(f"📦 Instalando {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ {package} instalado correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar {package}: {e}")

def desinstalar_paquete(package):
    """Desinstala un paquete usando pip."""
    print(f"🗑 Desinstalando {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", package],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ {package} desinstalado correctamente.")
    except subprocess.CalledProcessError:
        print(f"ℹ️ {package} no estaba instalado o ya fue desinstalado.")

def obtener_version_paquete(package_name):
    """Obtiene la versión de un paquete instalado."""
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        return None
    try:
        module = importlib.import_module(package_name)
        return getattr(module, '__version__', 'desconocida')
    except Exception:
        return None

def es_version_mayor_a_2(version):
    """Verifica si la versión es >= 2.0"""
    if version == 'desconocida':
        return False
    try:
        major = int(version.split('.')[0])
        return major >= 2
    except:
        return False

def main():
    print("🔧 Corrigiendo error de numpy 2.x incompatible con Streamlit")
    print("----------------------------------------------------------")

    # 1. Verificar versión actual de numpy
    numpy_version = obtener_version_paquete("numpy")
    if numpy_version:
        print(f"🔢 Versión actual de numpy: {numpy_version}")
        if es_version_mayor_a_2(numpy_version):
            print("⚠️ Se detectó numpy >= 2.0. Corrigiendo...")
            desinstalar_paquete("numpy")
            instalar_paquete("numpy==1.26.4")
        else:
            print("✅ numpy ya es compatible (versión < 2.0). No se requiere acción.")
    else:
        print("🔢 numpy no está instalado. Instalando versión compatible...")
        instalar_paquete("numpy==1.26.4")

    # 2. Reinstalar dependencias clave para asegurar compatibilidad
    print("\n🔧 Reinstalando dependencias críticas...")
    dependencias = [
        "streamlit==1.29.0",
        "pandas==2.1.0",
        "plotly==5.18.0",
        "PyYAML==6.0",
        "jinja2==3.1.2",
        "weasyprint==59.0"
    ]

    for dep in dependencias:
        instalar_paquete(dep)

    # 3. Verificar instalación
    print("\n🔍 Verificando instalaciones...")
    paquetes_clave = ["numpy", "streamlit", "pandas", "weasyprint"]
    for pkg in paquetes_clave:
        version = obtener_version_paquete(pkg)
        if version:
            estado = "✅" if not (pkg == "numpy" and es_version_mayor_a_2(version)) else "❌"
            print(f"{estado} {pkg} v{version}")
        else:
            print(f"❌ {pkg} no está instalado")

    # 4. Mensaje final
    numpy_version_final = obtener_version_paquete("numpy")
    if numpy_version_final and not es_version_mayor_a_2(numpy_version_final):
        print("\n🎉 ¡CORRECCIÓN COMPLETADA CON ÉXITO!")
        print("Tu entorno ya es compatible con Streamlit y Raíces del Ser.")
        print("\nEjecuta tu app con:")
        print("   streamlit run streamlit_app.py")
    else:
        print("\n❌ La corrección falló. Revisa los errores anteriores.")

if __name__ == "__main__":
    main()