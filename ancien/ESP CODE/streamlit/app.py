import streamlit as st
import requests

st.title("Gestion des Logements")

# Afficher les logements existants
st.subheader("Liste des Logements")
response = requests.get("http://127.0.0.1:8000/api/logements")
if response.status_code == 200:
    logements = response.json()
    for logement in logements:
        st.write(f"**{logement['id']}** - {logement['adresse']}")
else:
    st.error("Impossible de récupérer les logements.")

# Ajouter un nouveau logement
st.subheader("Ajouter un Logement")
nom = st.text_input("Nom")
adresse = st.text_input("Adresse")

if st.button("Ajouter"):
    if nom and adresse:
        response = requests.post(
            "http://127.0.0.1:8000/api/logements",
            json={"nom": nom, "adresse": adresse}
        )
        if response.status_code == 200:
            st.success("Logement ajouté avec succès !")
            st.experimental_rerun()
        else:
            st.error("Erreur lors de l'ajout du logement.")
    else:
        st.warning("Veuillez remplir tous les champs.")
