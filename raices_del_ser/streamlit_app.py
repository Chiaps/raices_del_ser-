import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from weasyprint import HTML
from datetime import datetime
import os
import uuid
from jinja2 import Template

# === CONFIGURACIÓN DE PÁGINA ===
st.set_page_config(
    page_title="Raíces del Ser",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CARGA DE AUTENTICACIÓN ===
try:
    with open('auth.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("Archivo `auth.yaml` no encontrado. Asegúrate de crearlo.")
    st.stop()

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login('Iniciar sesión', 'main')

if authentication_status is False:
    st.error("Nombre de usuario o contraseña incorrectos")
if authentication_status is None:
    st.warning("Por favor, ingresa tu nombre de usuario y contraseña")
if authentication_status:
    # === CARGA DE CONEXIONES ===
    try:
        with open('conexiones.json', 'r', encoding='utf-8') as f:
            conexiones_data = json.load(f)
    except FileNotFoundError:
        st.error("Archivo `conexiones.json` no encontrado.")
        st.stop()

    nodes = list(set([c['source'] for c in conexiones_data] + [c['target'] for c in conexiones_data]))
    node_to_index = {node: i for i, node in enumerate(nodes)}
    n = len(nodes)
    adjacency = np.zeros((n, n))

    def add_link(a, b, value=1):
        if a in node_to_index and b in node_to_index:
            i, j = node_to_index[a], node_to_index[b]
            adjacency[i, j] = value
            adjacency[j, i] = value

    for link in conexiones_data:
        add_link(link['source'], link['target'], link['value'])

    # === CATEGORIZACIÓN DE NODOS ===
    def categorize_node(node):
        arcanos = ["El Mundo", "El Emperador", "La Justicia", "El Juicio", "El Colgado", "La Torre", "La Muerte", "Templanza", "La Fuerza", "El Carro", "La Estrella", "La Luna", "El Sol", "La Rueda de la Fortuna", "El Loco", "Cinco de Espadas", "Tres de Copas", "Cinco de Bastos"]
        if node in arcanos:
            return "Arcanos Mayores"
        if node in ["El Ancestro No Nombrado", "El Ángel del Linaje", "El Espíritu del Lugar", "La Gran Alma", "El Alma que Espera", "El Que Se Fue Temprano", "El Guardián del Umbral", "El Portador del Secreto", "El Renacido"]:
            return "Presencias del Más Allá"
        if "Frase" in node or any(p in node for p in ["Libero lo que no es mío", "Tengo permiso", "Te nombro", "Soy uno con todos", "Permiso para", "Mi amor nutre", "Tu deseo no murió", "Hablo lo que callé"]):
            return "Frases Sanadoras"
        if any(p in node for p in ["Acné", "Ansiedad", "Dolor", "Miedo", "Agotamiento", "Insomnio", "Vacío", "Conflicto", "Carga", "Parálisis", "Duelo"]):
            return "Síntomas / Emociones"
        return "Cartas Raíces del Ser"

    colors_map = {
        "Arcanos Mayores": "#4E79A7",
        "Cartas Raíces del Ser": "#F28E2B",
        "Síntomas / Emociones": "#E15759",
        "Frases Sanadoras": "#76B7B2",
        "Presencias del Más Allá": "#59A14F"
    }

    # === SIDEBAR ===
    st.sidebar.title(f"🌿 Bienvenido, {name}")
    authenticator.logout("Cerrar sesión", "sidebar")
    menu = st.sidebar.radio("Navegar", ["Tu Lectura", "Círculo de Presencias", "Proponer Conexión", "Historial"])

    # === TU LECTURA PERSONALIZADA ===
    if menu == "Tu Lectura":
        st.title("🃏 Tu Lectura Personalizada")

        if 'lectura_realizada' not in st.session_state:
            st.session_state.lectura_realizada = False

        if not st.session_state.lectura_realizada:
            st.write("Presiona el botón para realizar tu tirada.")
            if st.button("Realizar Tirada (3 cartas)"):
                import random
                mazo_principal = [n for n in nodes if categorize_node(n) == "Cartas Raíces del Ser"]
                seleccionadas = random.sample(mazo_principal, 3)
                st.session_state.lectura = seleccionadas
                st.session_state.lectura_realizada = True
                st.rerun()

        if st.session_state.lectura_realizada:
            lectura = st.session_state.lectura
            st.write("### Cartas obtenidas:")
            for carta in lectura:
                st.markdown(f"- **{carta}**")

            sources_p, targets_p, values_p = [], [], []
            for i in range(n):
                for j in range(n):
                    if adjacency[i, j] > 0:
                        nodo_i, nodo_j = nodes[i], nodes[j]
                        if nodo_i in lectura or nodo_j in lectura:
                            sources_p.append(nodo_i)
                            targets_p.append(nodo_j)
                            values_p.append(adjacency[i, j])

            if sources_p:
                fig_sankey = go.Figure(go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=0.5),
                        label=sources_p + targets_p,
                        color=[colors_map[categorize_node(n)] for n in sources_p + targets_p]
                    ),
                    link=dict(
                        source=[sources_p.index(n) for n in sources_p],
                        target=[len(sources_p) + targets_p.index(n) for n in targets_p],
                        value=values_p
                    )
                ))
                fig_sankey.update_layout(title_text="Tu Mapa de Sanación", font_size=10)
                st.plotly_chart(fig_sankey, use_container_width=True)

            if st.button("Generar Informe PDF"):
                try:
                    with open('templates/informe.html', 'r', encoding='utf-8') as f:
                        template_str = f.read()
                    template = Template(template_str)
                    fecha = datetime.now().strftime("%d/%m/%Y")
                    frases = [
                        "Libero lo que no es mío y recibo con gratitud lo que sí me pertenece.",
                        "Tengo permiso para ser feliz.",
                        "Te nombro, te honro, te doy un lugar en mi corazón."
                    ]
                    grafico_html = fig_sankey.to_html(include_plotlyjs='cdn', full_html=False)
                    html_out = template.render(
                        nombre=name,
                        fecha=fecha,
                        cartas=lectura,
                        frases=frases,
                        grafico=grafico_html
                    )
                    pdf_filename = f"informe_{username}_{uuid.uuid4().hex}.pdf"
                    HTML(string=html_out).write_pdf(pdf_filename)
                    st.session_state.pdf_file = pdf_filename
                    st.success("Informe generado exitosamente.")
                    with open(pdf_filename, "rb") as f:
                        st.download_button(
                            label="📥 Descargar PDF",
                            data=f,
                            file_name=pdf_filename,
                            mime="application/pdf"
                        )
                    mensaje = f"Hola, comparto mi lectura de Raíces del Ser."
                    whatsapp_url = f"https://wa.me/?text={mensaje}&app_absent=0"
                    st.markdown(f"[📤 Enviar por WhatsApp]({whatsapp_url})", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error al generar PDF: {str(e)}")

    # === CÍRCULO DE PRESENCIAS (GRUPAL) ===
    elif menu == "Círculo de Presencias":
        st.title("🌀 Círculo de Presencias Colectivo")
        st.write("Comparte una carta que represente tu estado actual.")

        if 'circulo_grupal' not in st.session_state:
            st.session_state.circulo_grupal = []

        carta_grupal = st.selectbox("Elige una carta", nodes, key="carta_grupal_select")
        if st.button("Unirme al círculo"):
            st.session_state.circulo_grupal.append({"usuario": name, "carta": carta_grupal})
            st.rerun()

        if st.session_state.circulo_grupal:
            df_circulo = pd.DataFrame(st.session_state.circulo_grupal)
            st.dataframe(df_circulo)
            fig = go.Figure(go.Chord(
                names=list(df_circulo['carta'].unique()),
                source=[i for i in range(len(df_circulo))],
                target=[list(df_circulo['carta'].unique()).index(c) for c in df_circulo['carta']],
                value=[1]*len(df_circulo),
                colors=[colors_map[categorize_node(c)] for c in df_circulo['carta']]
            ))
            fig.update_layout(title="Presencias del Grupo")
            st.plotly_chart(fig, use_container_width=True)

    # === PROPONER NUEVA CONEXIÓN ===
    elif menu == "Proponer Conexión":
        st.title("🤝 Proponer Nueva Conexión Simbólica")
        col1, col2 = st.columns(2)
        with col1:
            source = st.selectbox("Origen", nodes, key="source_new")
        with col2:
            target = st.selectbox("Destino", nodes, key="target_new")
        descripcion = st.text_area("Descripción de la conexión (ej: 'El Colgado se relaciona con Acné por purificación interna')")
        if st.button("Enviar Propuesta"):
            propuesta = {
                "source": source,
                "target": target,
                "value": 1,
                "proponente": username,
                "descripcion": descripcion,
                "fecha": datetime.now().isoformat()
            }
            os.makedirs('data', exist_ok=True)
            with open('data/propuestas.jsonl', 'a', encoding='utf-8') as f:
                f.write(json.dumps(propuesta, ensure_ascii=False) + '\n')
            st.success("Propuesta enviada. Será revisada por el equipo.")

    # === HISTORIAL DE USUARIO ===
    elif menu == "Historial":
        st.title("📜 Tu Historial de Lecturas")
        if 'pdf_file' in st.session_state and os.path.exists(st.session_state.pdf_file):
            st.write("Último informe generado:")
            with open(st.session_state.pdf_file, "rb") as f:
                st.download_button(
                    "Descargar último PDF",
                    f,
                    st.session_state.pdf_file,
                    "application/pdf"
                )
        else:
            st.info("Aún no has generado ningún informe.")

    # === GUARDADO DE SESIÓN DE USUARIOS (opcional) ===
    if authentication_status:
        if 'usuarios_data' not in st.session_state:
            st.session_state.usuarios_data = {}