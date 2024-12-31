document.addEventListener("DOMContentLoaded", () => {
    const logementList = document.getElementById("logement-list");
    const addLogementBtn = document.getElementById("add-logement-btn");
    const modal = document.getElementById("modal");
    const closeModalBtn = document.getElementById("close-modal");
    const addLogementForm = document.getElementById("add-logement-form");

    // Fonction pour récupérer les logements
    async function fetchLogements() {
        try {
            const response = await fetch("/api/logements");
            const logements = await response.json();

            logementList.innerHTML = "";
            logements.forEach(logement => {
                const card = document.createElement("div");
                card.className = "logement-card";
                card.textContent = logement.adresse;
                logementList.appendChild(card);
            });
        } catch (error) {
            console.error("Erreur lors de la récupération des logements :", error);
        }
    }

    // Ouvrir le modal
    addLogementBtn.addEventListener("click", () => {
        modal.classList.remove("hidden");
    });

    // Fermer le modal
    closeModalBtn.addEventListener("click", () => {
        modal.classList.add("hidden");
    });

    // Ajouter un logement
    addLogementForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = new FormData(addLogementForm);
        const nom = formData.get("nom");
        const adresse = formData.get("adresse");

        try {
            const response = await fetch("/api/logements", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ nom, adresse })
            });

            if (response.ok) {
                alert("Logement ajouté avec succès !");
                modal.classList.add("hidden");
                fetchLogements(); // Recharger la liste des logements
                addLogementForm.reset();
            } else {
                alert("Erreur lors de l'ajout du logement.");
            }
        } catch (error) {
            console.error("Erreur :", error);
            alert("Erreur lors de l'ajout du logement.");
        }
    });

    // Chargement initial
    fetchLogements();
});
