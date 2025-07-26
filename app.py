import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import io

# Configuration de la page
st.set_page_config(
    page_title="ÊtrePROF - Personnalisation ML",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL de l'API Cloud Run (à adapter selon votre déploiement)
API_BASE_URL = st.secrets["api"]["API_URL"] # Remplacez par votre URL d'API

# Fonctions utilitaires pour l'API
def call_api(endpoint, method="GET", data=None):
    """Appelle l'API et gère les erreurs"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erreur API: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Erreur de connexion: {str(e)}")
        return None

# Interface principale
def main():
    # Header principal
    st.markdown("""
    # 🎓 ÊtrePROF - Personnalisation ML
    ### Dashboard de classification de contenu, clustering utilisateurs et recommandations personnalisées
    """)

    # Test de connexion API
    api_status = call_api("/")
    if api_status:
        st.success(f"✅ API connectée: {api_status.get('status', 'running')}")
    else:
        st.error("❌ Impossible de se connecter à l'API")
        st.stop()

    # Sidebar pour navigation
    st.sidebar.title("🧭 Navigation")
    section = st.sidebar.selectbox(
        "Choisir une section:",
        ["📝 Classification de contenu", "👥 Clusters utilisateurs", "🎯 Recommandations", "👤 Profil utilisateur"]
    )

    # Section 1: Classification de contenu
    if section == "📝 Classification de contenu":
        st.header("📝 Classification de contenu")
        st.markdown("Analysez le contenu markdown pour identifier automatiquement le thème et le défi prioritaire.")

        # Zone de texte pour le contenu
        content_input = st.text_area(
            "Collez votre contenu markdown ici:",
            height=200,
            placeholder="""# Enseigner les mathématiques au collège

## Stratégies pour l'apprentissage différencié

Les élèves ont des rythmes d'apprentissage différents...
"""
        )

        col1, col2 = st.columns([1, 4])
        with col1:
            analyze_btn = st.button("🔍 Analyser le contenu", type="primary")

        if analyze_btn and content_input.strip():
            with st.spinner("Analyse en cours..."):
                result = call_api("/classify", method="POST", data={"content": content_input})

                if result and result.get("success"):
                    data = result["data"]

                    # Affichage des résultats
                    st.success("✅ Analyse terminée !")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("🎯 Thème principal", data["theme"])
                    with col2:
                        st.metric("⚡ Défi prioritaire", data["defi"])

                    # Affichage sous forme de carte
                    st.markdown("### 📊 Résultats détaillés")
                    st.json(data)

        elif analyze_btn:
            st.warning("⚠️ Veuillez saisir du contenu à analyser")

    # Section 2: Clusters utilisateurs
    elif section == "👥 Clusters utilisateurs":
        st.header("👥 Clusters utilisateurs")
        st.markdown("Visualisation des 4 clusters comportementaux et recalcul en temps réel.")

        # Récupération des informations de clusters
        clusters_data = call_api("/clusters")

        if clusters_data and clusters_data.get("success"):
            clusters = clusters_data["clusters"]

            # Métriques globales
            st.markdown("### 📈 Vue d'ensemble des clusters")

            cluster_names = []
            cluster_counts = []
            cluster_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']

            cols = st.columns(4)
            for i, (cluster_id, cluster_info) in enumerate(clusters.items()):
                cluster_names.append(cluster_info["name"])
                cluster_counts.append(cluster_info.get("count", 0))

                with cols[i]:
                    st.metric(
                        f"🏷️ {cluster_info['name']}",
                        f"{cluster_info.get('count', 0):,} utilisateurs"
                    )

            # Graphique en secteurs
            st.markdown("### 🥧 Distribution des clusters")
            fig_pie = px.pie(
                values=cluster_counts,
                names=cluster_names,
                title="Répartition des utilisateurs par cluster",
                color_discrete_sequence=cluster_colors
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

            # Profils comportementaux détaillés
            st.markdown("### 🔍 Profils comportementaux détaillés")

            selected_cluster = st.selectbox(
                "Sélectionner un cluster pour voir le détail:",
                options=list(clusters.keys()),
                format_func=lambda x: f"Cluster {x}: {clusters[x]['name']}"
            )

            if selected_cluster:
                cluster_profile = clusters[selected_cluster]["profile"]

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"#### 📊 {clusters[selected_cluster]['name']}")

                    # Métriques principales
                    key_metrics = {
                        "Fiches outils": cluster_profile.get("nb_fiche_outils", 0),
                        "Guides pratiques": cluster_profile.get("nb_guide_pratique", 0),
                        "Total interactions": cluster_profile.get("total_interactions_x", 0),
                        "Diversité contenus": cluster_profile.get("diversite_contenus", 0)
                    }

                    for metric, value in key_metrics.items():
                        st.metric(metric, f"{value:.2f}" if isinstance(value, float) else value)

                with col2:
                    # Graphique radar des comportements
                    categories = ["Fiches outils", "Guides pratiques", "Votes", "Commentaires", "Emails ouverts"]
                    values = [
                        cluster_profile.get("nb_fiche_outils", 0),
                        cluster_profile.get("nb_guide_pratique", 0),
                        cluster_profile.get("nb_vote", 0),
                        cluster_profile.get("nb_comments", 0),
                        cluster_profile.get("nb_opened_mail", 0)
                    ]

                    fig_radar = go.Figure()
                    fig_radar.add_trace(go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill='toself',
                        name=clusters[selected_cluster]['name'],
                        line_color=cluster_colors[int(selected_cluster)]
                    ))

                    fig_radar.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, max(values) * 1.1] if max(values) > 0 else [0, 1]
                            )),
                        showlegend=False,
                        title=f"Profil comportemental - {clusters[selected_cluster]['name']}"
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)

            # Bouton de recalcul
            st.markdown("### 🔄 Recalcul des clusters")
            st.info("💡 Cette opération recalcule tous les clusters en temps réel basés sur les dernières données utilisateurs.")

            if st.button("🚀 Recalculer les clusters", type="secondary"):
                with st.spinner("Recalcul en cours... Cela peut prendre quelques minutes."):
                    recompute_result = call_api("/clusters/recompute", method="POST")

                    if recompute_result and recompute_result.get("success"):
                        st.success("✅ Clusters recalculés avec succès !")

                        # Affichage des nouveaux résultats
                        st.markdown("#### 📊 Nouvelle distribution:")
                        distribution = recompute_result["cluster_distribution"]

                        cols = st.columns(4)
                        for i, (cluster_key, count) in enumerate(distribution.items()):
                            with cols[i]:
                                st.metric(f"Cluster {i}", f"{count:,}")

                        st.balloons()
                        st.rerun()  # Rafraîchir l'interface

    # Section 3: Recommandations
    elif section == "🎯 Recommandations":
        st.header("🎯 Recommandations par cluster")
        st.markdown("Stratégies de contenu personnalisées selon le profil comportemental de chaque cluster.")

        # Sélection du cluster
        cluster_options = {
            0: "Balanced Users",
            1: "Email Specialists",
            2: "Super Users",
            3: "Inactive Users"
        }

        selected_cluster_id = st.selectbox(
            "Choisir un cluster:",
            options=list(cluster_options.keys()),
            format_func=lambda x: f"Cluster {x}: {cluster_options[x]}"
        )

        if st.button("🎯 Obtenir les recommandations", type="primary"):
            with st.spinner("Génération des recommandations..."):
                recommendations = call_api(f"/recommend/{selected_cluster_id}")

                if recommendations and recommendations.get("success"):
                    rec_data = recommendations["recommendations"]

                    # En-tête du cluster
                    st.markdown(f"### 🏷️ {rec_data['cluster_name']}")

                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.markdown("#### 🎯 Stratégie recommandée")
                        st.info(rec_data["strategy"])

                        st.markdown("#### 📝 Description du cluster")
                        st.write(rec_data["description"])

                        st.markdown("#### 🚀 Prochaines étapes")
                        st.write(rec_data.get("next_steps", "À définir"))

                    with col2:
                        st.markdown("#### 📊 Types de contenu recommandés")
                        for content_type in rec_data["recommended_content_types"]:
                            st.markdown(f"• {content_type}")

                        st.markdown("#### 🎪 Approche d'engagement")
                        st.write(rec_data["engagement_approach"])

                    # Status et avertissement
                    if recommendations.get("status"):
                        st.warning(f"ℹ️ {recommendations['status']}")

        # Vue d'ensemble de toutes les recommandations
        if st.button("📋 Voir toutes les recommandations"):
            st.markdown("### 📊 Stratégies pour tous les clusters")

            all_recommendations = {}

            for cluster_id in range(4):
                rec_result = call_api(f"/recommend/{cluster_id}")
                if rec_result and rec_result.get("success"):
                    all_recommendations[cluster_id] = rec_result["recommendations"]

            if all_recommendations:
                # Tableau comparatif
                comparison_data = []
                for cluster_id, rec in all_recommendations.items():
                    comparison_data.append({
                        "Cluster": f"{cluster_id}: {rec['cluster_name']}",
                        "Stratégie": rec["strategy"],
                        "Approche": rec["engagement_approach"],
                        "Types de contenu": ", ".join(rec["recommended_content_types"][:2]) + "..."
                    })

                df_comparison = pd.DataFrame(comparison_data)
                st.dataframe(df_comparison, use_container_width=True)

    # Section 4: Profil utilisateur
    elif section == "👤 Profil utilisateur":
        st.header("👤 Lookup profil utilisateur")
        st.markdown("Recherchez un utilisateur spécifique pour voir son cluster et ses recommandations personnalisées.")

        col1, col2 = st.columns([2, 1])

        with col1:
            user_id = st.number_input(
                "ID Utilisateur:",
                min_value=1,
                value=12345,
                step=1,
                help="Entrez l'identifiant numérique de l'utilisateur"
            )

        with col2:
            search_btn = st.button("🔍 Rechercher le profil", type="primary")

        if search_btn:
            with st.spinner(f"Recherche du profil utilisateur {user_id}..."):
                profile_result = call_api(f"/user/{user_id}/profile")

                if profile_result and profile_result.get("success"):
                    profile_data = profile_result["data"]

                    # Informations générales
                    st.success(f"✅ Utilisateur {user_id} trouvé !")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("👤 ID Utilisateur", profile_data["user_id"])

                    with col2:
                        cluster_info = profile_data["cluster"]
                        st.metric("🏷️ Cluster", f"{cluster_info['id']}: {cluster_info['name']}")

                    with col3:
                        # Calculer un score d'engagement basé sur le profil
                        profile = profile_data["profile"]
                        engagement_score = (
                            profile.get("anciennete", 0) * 2 +
                            profile.get("degre", 0) * 10
                        ) / 10
                        st.metric("📊 Score engagement", f"{engagement_score:.1f}/10")

                    # Profil détaillé
                    st.markdown("### 📋 Profil détaillé")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("#### 🎓 Informations pédagogiques")
                        profile_info = profile_data["profile"]

                        st.write(f"**Ancienneté:** {profile_info.get('anciennete', 'N/A')} années")
                        st.write(f"**Degré:** {profile_info.get('degre', 'N/A')}")
                        st.write(f"**Académie:** {profile_info.get('academie', 'N/A')}")

                        if profile_info.get('niveaux_enseignes'):
                            niveaux = profile_info['niveaux_enseignes']
                            if isinstance(niveaux, list):
                                st.write(f"**Niveaux enseignés:** {', '.join(niveaux)}")
                            else:
                                st.write(f"**Niveaux enseignés:** {niveaux}")

                    with col2:
                        st.markdown("#### 🎯 Recommandations personnalisées")
                        recommendations = profile_data["recommendations"]

                        st.info(f"**Stratégie:** {recommendations['strategy']}")

                        st.markdown("**Types de contenu recommandés:**")
                        for content_type in recommendations["recommended_content_types"]:
                            st.markdown(f"• {content_type}")

                    # Visualisation du cluster
                    st.markdown("### 📊 Position dans le cluster")

                    # Créer un graphique simple montrant la position de l'utilisateur
                    cluster_id = cluster_info['id']
                    cluster_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']

                    fig = go.Figure()

                    # Ajouter les 4 clusters
                    clusters_sizes = [15234, 8756, 2341, 28408]  # Données exemple
                    cluster_names = ["Balanced Users", "Email Specialists", "Super Users", "Inactive Users"]

                    fig.add_trace(go.Bar(
                        x=cluster_names,
                        y=clusters_sizes,
                        marker_color=[cluster_colors[i] if i != cluster_id else '#FFD700' for i in range(4)],
                        text=[f"Votre cluster" if i == cluster_id else "" for i in range(4)],
                        textposition="auto"
                    ))

                    fig.update_layout(
                        title=f"Position de l'utilisateur {user_id} dans les clusters",
                        xaxis_title="Clusters",
                        yaxis_title="Nombre d'utilisateurs",
                        showlegend=False
                    )

                    st.plotly_chart(fig, use_container_width=True)

                elif profile_result and not profile_result.get("success"):
                    st.error(f"❌ {profile_result.get('error', 'Utilisateur non trouvé')}")
                else:
                    st.error("❌ Erreur lors de la recherche du profil")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        🎓 ÊtrePROF ML Dashboard - Développé par Ecolhuma<br>
        API Status: ✅ Connectée | Version: 1.0.0
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
